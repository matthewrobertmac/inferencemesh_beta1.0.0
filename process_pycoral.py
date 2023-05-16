import subprocess
from google.cloud import storage

# Define constants
GCS_BUCKET = "raspberrypi4"
PREFIX = "processed_"
GOOGLE_CLOUD_PROJECT = "pullupnyc"  # replace with your actual project id

# Instantiate a Google Cloud Storage client
client = storage.Client(GOOGLE_CLOUD_PROJECT)

# Access the bucket
bucket = client.bucket(GCS_BUCKET)

# Define the model and labels for Google Coral Edge TPU
model = "ssd_mobilenet_v2_coco_quant_no_nms_edgetpu.tflite"  # replace with your model path
labels = "coco_labels.txt"  # replace with your labels path

def process_image_with_google_coral_edge_tpu(image_path, model, labels):
    # Define the command as a list of strings
    cmd = [
        "python3", 
        "small_object_detection.py",
        "--model", model,
        "--label", labels,
        "--input", image_path,
        "--tile_size", "1352x900,500x500,250x250",
        "--tile_overlap", "50",
        "--score_threshold", "0.25",
        "--output", f"processed_{image_path}"
    ]

    # Run the command
    subprocess.run(cmd, check=True)

    # Return the path of the processed image
    return f"processed_{image_path}"

# Iterate over all images in the bucket
blobs = bucket.list_blobs()

for blob in blobs:
    # Only process if image hasn't been processed before
    if not blob.name.startswith(PREFIX):
        # Download the image to local
        blob.download_to_filename(blob.name)
        
        # Process the image
        processed_image = process_image_with_google_coral_edge_tpu(blob.name, model, labels)

        # Save the processed image back to the bucket with a prefix
        new_blob = bucket.blob(PREFIX + blob.name)
        new_blob.upload_from_filename(processed_image)

