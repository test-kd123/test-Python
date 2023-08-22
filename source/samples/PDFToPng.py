import yaml
from compdfkit.client import CPDFClient
from compdfkit.enums import CPDFConversionEnum
from compdfkit.param.CPDFToPngParameter import CPDFToPngParameter
from compdfkit.constant import CPDFConstant


yaml_path = "properties.yaml"
yaml_file = open(yaml_path, 'r')
properties = yaml.safe_load(yaml_file)
public_key = properties["public_key"]
secret_key = properties["secret_key"]
client = CPDFClient(public_key, secret_key)


def pdf_to_png():
    # Create Task
    create_task_result = client.create_task(CPDFConversionEnum.PDF_TO_PNG)
    # TaskId
    task_id = create_task_result.task_id
    # Upload File
    file = properties["file"]
    file_password = ""
    file_parameter = CPDFToPngParameter()
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
    pdf_to_png()
