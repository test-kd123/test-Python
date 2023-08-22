"""
ComPDFKit API Libraries Client Module

This module is responsible for making the http requests to the ComPDFKit api.
You can use this module to implement ComPDFKit's PDF page editing, document format conversion,
and image recognition API calls.

Dependencies:
    requests: Handles the http requests.
    requests_toolbelt: Handles the multipart/form-data requests.
    time: Handles the time related operations.
    os: Handles the file related operations.
"""
import requests
import time
import os

from requests_toolbelt import MultipartEncoder


from .pojo.compdfkit import CPDFOauthResult, CPDFCreateTaskResult, CPDFUploadFileResult, CPDFTaskInfoResult
from .pojo.compdfkit import CPDFTool, CPDFFileInfo

from .constant import CPDFConstant, CPDFLanguageConstant

from .enums import CPDFConversionEnum, CPDFDocumentAIEnum, CPDFDocumentEditorEnum
from .exception import CPDFException


class CPDFClient:
    """
        For executing the ComPDFKit API calls
    """
    _http_client = None

    def __init__(self, public_key, secret_key, connection_timeout=-1):
        """
        :type public_key: str
        :type secret_key: str
        :type connection_timeout: int
        :param public_key: The public key of the ComPDFKit api.
        :param secret_key: The secret key of the ComPDFKit api.
        :param connection_timeout: The connection timeout limit. Default: -1.
        """
        self._http_client = CPDFHttpClient(public_key, secret_key, connection_timeout)

    def _get_compdfkit_auth(self, public_key, secret_key):
        return self._http_client.get_compdfkit_auth(public_key, secret_key)

    def get_tools(self):
        """
        This interface is used to obtain the collection of all PDF tools supported by the ComPDFKit API,
        and you can query the URL of each PDF tool.

        :return: The list of tools that are enabled for the user.
        """
        return self._http_client.get_tools()

    def get_file_info(self, file_key, language=None):
        """
        Get the download link of the corresponding result file according to the filekey of each file.

        :type file_key: str
        :param file_key: The key of the file.
        :type language: int
        :param language: The log language. Default: English.
        :return: The information of the file.
        """
        return self._http_client.get_file_info(file_key, language=language)

    def get_asset_info(self):
        """
        Get the remaining assets of the current user.

        :return: The information of the asset.
        """
        return self._http_client.get_asset_info()

    def get_task_list(self, page, size):
        """
        Request the current user file transfer task list.

        :type page: str
        :param page: The page number of the task list.
        :type size: str
        :param size: The size of a page.
        :return: The list page of the task list.
        """
        return self._http_client.get_task_list(page, size)

    def create_task(self, task_object, language=CPDFLanguageConstant.ENGLISH):
        """
        A task ID is automatically generated for you based on the type of PDF tool you choose.
        You can provide the callback notification URL. After the task processing is completed,
        we will notify you of the task result through the callback interface.
        You can perform other operations according to the task result, such as downloading the result file.

        :type task_object: Any
        :param language: CPDFLanguageConstant
        :param task_object: The task type or url of the task.
                            The object type can be CPDFConversionEnum, CPDFDocumentAIEnum, CPDFDocumentEditorEnum, str.
        :param language: The language of log information. Default: English.
        :return: The task id.
        """
        if isinstance(task_object, str):
            return self._http_client.create_task(task_object, language=language)
        elif (isinstance(task_object, CPDFConversionEnum) or
              isinstance(task_object, CPDFDocumentAIEnum) or
              isinstance(task_object, CPDFDocumentEditorEnum)):
            return self.create_task(task_object.value)
        else:
            raise CPDFException(cause="The task object is not a valid type.")

    def upload_file(self, file, task_id, password=None, file_parameter=None,
                    image=None, image_file_name=None):
        """
        Upload the original file and bind the file to the task ID.
        The field parameter is used to pass the JSON string to set the processing parameters for the file.
        Each file will generate automatically a unique filekey.
        Please note that a maximum of five files can be uploaded for a task ID
        and no files can be uploaded for that task after it has started.

        :type file: str
        :type task_id: str
        :type password: str
        :type file_parameter: CPDFFileParameter
        :type image: str
        :type image_file_name: str
        :param file: The file path to be uploaded.
        :param task_id: The id of the task.
        :param password: The password of the PDF file.
        :param file_parameter: The parameters of the task.
        :param image: The image path to be uploaded.
        :param image_file_name: The name of the image file.
        :return: The result of the upload.
        """
        return self._get_upload_file_result(file=file, task_id=task_id, password=password,
                                            file_parameter=file_parameter, image=image, image_file_name=image_file_name)

    def _get_upload_file_result(self, file, task_id, password=None, file_parameter=None,
                                image=None, image_file_name=None):
        (file_path, file_name) = os.path.split(file)

        if image_file_name is None:
            (image_path, image_file_name) = os.path.split(image)

        return self._http_client.get_upload_file_result(file=file, task_id=task_id, password=password,
                                                        file_parameter=file_parameter, file_name=file_name, image=image,
                                                        image_file_name=image_file_name)

    def execute_task(self, task_id):
        """
        After the file upload is completed, call this interface with the task ID to process file.

        :type task_id: str
        :param task_id: The id of the task.
        :return: The result of the task.
        """
        return self._http_client.execute_task(task_id)

    def get_task_info(self, task_id):
        """
        Request task status and file-related metadata based on the task ID.

        :type task_id: str
        :param task_id: The id of the task.
        :return: The information of the task.
        """
        return self._http_client.get_task_info(task_id)


class CPDFHttpClient:
    """
        This class is responsible for making the http requests to the ComPDFKit api.
    """

    ADDRESS = "https://api-server.compdf.com/server/"
    _connect_timeout = -1

    def __init__(self, public_key, secret_key, connection_timeout=-1):
        """
        :type public_key: str
        :type secret_key: str
        :param public_key: The public key of the ComPDFKit api.
        :param secret_key: The secret key of the ComPDFKit api.
        """
        self._expire_time = -1
        self._access_token = ""
        self._public_key = public_key
        self._secret_key = secret_key
        self._connect_timeout = connection_timeout
        self.refresh_access_token()

    def _basic_headers(self):
        header = {"Authorization": "Bearer " + self._access_token}
        return header

    def get_access_token(self):
        """

        :return: The access token of the ComPDFKit api.
        """
        if self._expire_time < 0 or self._expire_time < int(round(time.time() * 1000)) or self._access_token == "":
            self.refresh_access_token()

        return self._access_token

    def set_access_token(self, access_token, expires_in):
        """
        :type access_token: str
        :param access_token: The access token of the ComPDFKit api.
        :type expires_in: int
        :param expires_in: The expiration of the access token.
        """
        self._access_token = access_token
        self._expire_time = expires_in * 1000 + int(round(time.time() * 1000))

    def refresh_access_token(self):
        """
        Refreshes the access token.
        """
        new_token = self.get_compdfkit_auth(self._public_key, self._secret_key)
        self.set_access_token(new_token.access_token, int(new_token.expires_in))

    def get_compdfkit_auth(self, public_key, secret_key):
        """
        :type public_key: str
        :type secret_key: str
        :param public_key: The public key of the ComPDFKit api.
        :param secret_key: The secret key of the ComPDFKit api.
        :return: The result of the authentication. Type: CPDFOauthResult
        """
        url = self.ADDRESS + CPDFConstant.API_V1_OAUTH_TOKEN
        headers = {"Content-Type": "application/json"}
        data = {"publicKey": public_key, "secretKey": secret_key}

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            print(response.json())
            return CPDFOauthResult(response.json()['data'])
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def get_tools(self):
        """
        :return: The enable tools of the ComPDFKit api. Type: list[CPDFTool]
        """
        url = self.ADDRESS + CPDFConstant.API_V1_TOOL_SUPPORT
        response = requests.get(url)
        if response.status_code == 200:
            result = []
            for tool in response.json()['data']:
                result.append(CPDFTool(tool))
            return result
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def get_file_info(self, file_key, language=CPDFLanguageConstant.ENGLISH):
        """
        :type file_key: str
        :param file_key: The file key of the file.
        :type language: int
        :param language: The language of the logout. Default: English.
        :return: The file info of the file.
        """
        url = self.ADDRESS + CPDFConstant.API_V1_FILE_INFO
        params = {
            "fileKey": file_key, "language": language
        }
        response = requests.get(url, headers=self._basic_headers(), params=params)

        if response.status_code == 200:
            print(response.json())
            return CPDFFileInfo(response.json()["data"])
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def get_asset_info(self):
        """
        :return: The assert info of the ComPDFKit api.
        """
        url = self.ADDRESS + CPDFConstant.API_V1_ASSET_INFO
        response = requests.get(url, headers=self._basic_headers())
        if response.status_code == 200:
            print(response.json()["data"])
            return response.json()['data']
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def get_task_list(self, page="1", size="5"):
        """
        :type page: str
        :param page: The page number of the task list.
        :type size: str
        :param size: The page size of the task list.
        :return: The task list of the ComPDFKit api.
        """
        url = self.ADDRESS + CPDFConstant.API_V1_TASK_LIST
        params = {"page": page, "pageSize": size}
        response = requests.get(url, headers=self._basic_headers(), params=params)
        if response.status_code == 200:
            print(response.json()["data"])
            return response.json()['data']
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def create_task(self, execute_type_url, language=CPDFLanguageConstant.ENGLISH):
        """
        :type language: int
        :param language: The language of the logout. Default: English.
        :type execute_type_url: str
        :param execute_type_url: The execute type url of the task.
        :return: The task id of the task.
        """
        url = self.ADDRESS + CPDFConstant.API_V1_CREATE_TASK.format(executeTypeUrl=execute_type_url)
        params = {"language": language}

        response = requests.get(url, headers=self._basic_headers(), params=params)
        if response.status_code == 200:
            print(response.json()["data"])
            return CPDFCreateTaskResult(response.json()['data'])
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def get_upload_file_result(self, file, task_id, password=None, file_parameter=None, file_name=None,
                               image=None, image_file_name=None, language=CPDFLanguageConstant.ENGLISH):
        """
        :type file: str
        :param file: The path of the file.
        :param task_id: The id of the task.
        :param password: The password of the PDF file.
        :type file_parameter: CPDFFileParameter
        :param file_parameter: The parameters of the task.
        :param file_name:
        :param image:
        :param image_file_name:
        :type language: int
        :param language: The language of the logout. Default: English.
        :return:
        """
        url = self.ADDRESS + CPDFConstant.API_V1_UPLOAD_FILE

        if task_id is None:
            raise CPDFException(cause="The task id is required.")

        if file_name is None:
            (file_path, file_name) = os.path.split(file)

        file_request_body = (file_name, open(file, "rb"))

        params = {
            "taskId": task_id,
            "file": file_request_body,
            "language": str(language)
        }
        if password:
            params["password"] = password
        if file_parameter:
            parameter_json = file_parameter.to_cpdf_json_str()
            params["parameter"] = parameter_json

        if image and image_file_name:
            params["image"] = (image_file_name, open(image, "rb"))

        headers = self._basic_headers()

        data = MultipartEncoder(params)
        headers["Content-Type"] = data.content_type
        response = requests.post(url, data=data, headers=headers)
        if response.status_code == 200:
            print(response.json()["data"])
            return CPDFUploadFileResult(response.json()['data'])
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def execute_task(self, task_id, language=CPDFLanguageConstant.ENGLISH):
        """
        :type task_id: str
        :param task_id: The task id of the task.
        :type language: int
        :param language: The language of the logout. Default: English.
        :return: The result of the execution.
        """
        url = self.ADDRESS + CPDFConstant.API_V1_EXECUTE_TASK
        params = {
            "taskId": task_id,
            "language": language
        }

        response = requests.get(url, headers=self._basic_headers(), params=params)
        if response.status_code == 200:
            print(response.json()["data"])
            return CPDFCreateTaskResult(response.json()['data'])
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])

    def get_task_info(self, task_id, language=CPDFLanguageConstant.ENGLISH):
        """
        :type task_id: str
        :param task_id: The task id of the task.
        :return: The result of the task info.
        """
        url = self.ADDRESS + CPDFConstant.API_V1_TASK_INFO
        params = {
            "taskId": task_id,
            "language": language
        }
        response = requests.get(url, headers=self._basic_headers(), params=params)
        if response.status_code == 200:
            print(response.json()["data"])
            return CPDFTaskInfoResult(response.json()['data'])
        else:
            raise CPDFException(code=response.json()['code'], message=response.json()['msg'])
