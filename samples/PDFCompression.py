from compdfkit.client import CPDFClient
from compdfkit.enums import CPDFDocumentEditorEnum
from compdfkit.param  import CPDFCompressParameter
from compdfkit.constant import CPDFConstant


public_key = ""
secret_key = ""
client = CPDFClient(public_key, secret_key)


def page_compression():
    # Create Task
    create_task_result = client.create_task(CPDFDocumentEditorEnum.COMPRESS)
    # TaskId
    task_id = create_task_result.task_id
    # Upload File
    file = "sample/test.pdf"
    file_password = ""
    file_parameter = CPDFCompressParameter()
    file_parameter.quality = "50"
    upload_file_result = client.upload_file(file, task_id, file_password, file_parameter)
    file_key = upload_file_result.file_key
    # Perform tasks
    client.execute_task(task_id)
    # Get task processing information
    task_info = client.get_task_info(task_id)
    # Determine whether the task status is "TaskFinish"
    if task_info.task_status == CPDFConstant.TASK_FINISH:
        print(task_info)
        # Get the final file processing information
        file_info = client.get_file_info(file_key)
        print(file_info)
        # If the task is finished, cancel the scheduled task
    else:
        print("Task incomplete processing")


if __name__ == "__main__":
    page_compression()