import boto3
from flask import Flask, render_template, request

app = Flask(__name__)
rekognition = boto3.client('rekognition')
S3 = boto3.client('s3')
dynamodb = boto3.client('dynamodb')

#landing oage route
@app.route('/')
def index():
    """
    Renders the index.html template.

    Returns:
        The rendered index.html template.
    """
    return render_template('index.html')

@app.route("/addUser")
def addUser():
    """
    Renders the addUser.html template.

    Returns:
        The rendered addUser.html template.
    """
    return render_template("addUser.html")


#upload image route
@app.route("/upload", methods=["POST"])
def upload():
    """
    Handle the file upload and perform image matching with a collection.

    Returns:
        str: The rendered HTML template with the matched information and file details.
    """
    if "file" not in request.files:
        return "file not found"
    
    file = request.files["file"]
    
    if file.filename == "":
        return "file not found"
    
    #get details of uploaded file
    filename = file.filename
    file.save("./visitors/"+filename)

    
    #add visitor to another s3 bucket
    if add_visitor_to_bucket(filename):
        addSuccess = "visitor added successfully"

    #match image with images in collection

    with open("./visitors/" + filename, "rb") as file:
        image_bytes = file.read()

    CollectionId = "employee"
    matched_info = match_image_with_collection(image_bytes, CollectionId)

    #get details from dynamodb
    table_name = "ayush-employee-table"

    if matched_info:
        face_id = matched_info[0]["Face"]["FaceId"]
        first_name, last_name = get_name_from_dynamodb(table_name, face_id)

    else:
        first_name, last_name = "Unknown", "Unknown"

    return render_template("index.html", matched_info=matched_info, first_name=first_name, last_name=last_name, filename=filename, addSuccess=addSuccess)

def match_image_with_collection(image_bytes, CollectionId, threshold=80):
    """
    Matches an image with a collection of faces in Amazon Rekognition.

    Args:
        image_bytes (bytes): The image bytes to be matched.
        CollectionId (str): The ID of the collection containing the faces.
        threshold (int, optional): The minimum confidence threshold for a match. Defaults to 80.

    Returns:
        list: A list of face matches found in the collection.

    Raises:
        Exception: If there is an error while matching the image with the collection.
    """
    try:
        response = rekognition.search_faces_by_image(
            CollectionId=CollectionId,
            Image={
                "Bytes": image_bytes
            },
            FaceMatchThreshold=threshold,
            MaxFaces=1
        )
        face_match = response["FaceMatches"]
        return face_match
    
    except Exception as e:
        return f"Error matching image with collection: {e}"

def get_name_from_dynamodb(table_name, face_id):
    """
    Retrieves the first name and last name associated with a given face ID from DynamoDB.

    Args:
        table_name (str): The name of the DynamoDB table.
        face_id (str): The face ID to retrieve the name for.

    Returns:
        tuple: A tuple containing the first name and last name associated with the face ID.
               If the face ID is not found in the table, (None, None) is returned.
    """
    try:
        #get firstname and lastname from dynamodb
        response = dynamodb.get_item(
            TableName=table_name,
            Key={
                "rekID": {
                    "S": face_id
                }
            }
        )
        if "Item" in response:
            item = response["Item"]
            first_name = item.get("firstname", {}).get("S", "Unknown")
            last_name = item.get("lastname", {}).get("S", "Unknown")
            return first_name, last_name
        
        else:
            return None, None # first_name = None, last_name = None
    
    except Exception as e:
        print(f"Error getting name from dynamodb: {e}")
        return None, None # first_name = None, last_name = None
    
#route to store image in collection by uploadinf it to bucket and verifiy the naming convention
@app.route("/add_employee", methods=["POST", "GET"])
def add_employee():
    """
    Add a new employee to the system.

    This function handles the "/add_employee" route and allows users to add a new employee to the system.
    It expects a file to be uploaded with the request, verifies the naming convention of the file,
    saves the file to the local "visitors" directory, and uploads it to an S3 bucket.

    Returns:
        str: A message indicating the success or failure of the operation.
    """
    if "file" not in request.files:
        return "file not found"
    
    file = request.files["file"]
    
    if file.filename == "":
        return "file not found"
    
    #get details of uploaded file
    filename = file.filename
    file.save("./visitors/"+filename)

    #verify naming convention
    if not verify_naming_convention(filename):
        return "Invalid naming convention. Please follow the naming convention."
    
    #upload image to s3 bucket
    bucket_name = "ayush-employee-image-storage"
    key = filename
    S3.upload_file("./visitors/" + filename, bucket_name, key)


    return render_template("addUser.html", message="Employee added successfully")

def verify_naming_convention(filename):
    """
    Verify if the given filename follows the correct naming convention.

    The correct naming convention is: firstname_lastname.jpg

    Args:
        filename (str): The name of the file to be verified.

    Returns:
        bool: True if the filename follows the correct naming convention, False otherwise.
    """
    name, ext = filename.split(".")
    if "_" not in name:
        return False
    
    first_name, last_name = name.split("_")
    if not first_name or not last_name:
        return False
    
    return True

#function to add every new visitor to another s3 bucket for record
def add_visitor_to_bucket(filename):
    """
    Uploads a visitor image file to an S3 bucket.

    Args:
        filename (str): The name of the file to be uploaded.

    Returns:
        bool: True if the file was successfully uploaded, False otherwise.
    """
    bucket_name = "ayush-visitor-image-bucket"
    key = filename
    S3.upload_file("./visitors/" + filename, bucket_name, key)
    return True

if __name__ == "__main__":
    app.run(debug=True)


    

    