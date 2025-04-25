import os
import subprocess
import uuid
from PIL import Image
from time import sleep

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"
N_WORKERS = 4
CHUNKS_DIR = "/app/shared_volume"
DOCKER_IMAGE_NAME = "iarzaesteban94/worker:latest"

def delete_on_bucket(filename):
    gcs_input_path = f"gs://sobel-distribuido-images/input/{filename}"
    result = subprocess.run(["gsutil", "rm", gcs_input_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[MASTER] Deleted {gcs_input_path} from GCS", flush=True)
    else:
        print(f"[MASTER] Error deleting {gcs_input_path}: {result.stderr}", flush=True)

def split_image(image_path, chunks, output_dir):
    print(f"[MASTER] Procesando: {image_path}", flush=True)
    image = Image.open(image_path)
    width, height = image.size
    chunk_height = height // chunks
    for i in range(chunks):
        top = i * chunk_height
        bottom = (i + 1) * chunk_height if i < chunks - 1 else height
        cropped = image.crop((0, top, width, bottom))
        chunk_path = os.path.join(output_dir, f"chunk_{i}.png")
        cropped.save(chunk_path)
        print(f"[MASTER] Saved chunk {i} to {chunk_path}", flush=True)

def launch_worker(worker_id):
    unique_id = uuid.uuid4().hex[:6]
    container_name = f"worker_{worker_id}_{unique_id}"
    chunk_file = f"/app/shared_volume/chunk_{worker_id}.png"
    output_file = f"/app/shared_volume/processed_chunk_{worker_id}.png"
    
    command = [
        "docker", "run", "--rm", "--name", container_name,
        "-v", "/data/shared_volume:/app/shared_volume",
        DOCKER_IMAGE_NAME,
        "python", "worker.py", chunk_file, output_file
    ]

    print(f"[MASTER] Launching worker {worker_id} with container name {container_name}", flush=True)
    subprocess.Popen(command)

def wait_for_processed_chunks(num_chunks, output_dir):
    print("[MASTER] Waiting for all processed chunks...", flush=True)
    while True:
        processed = [
            f for f in os.listdir(output_dir)
            if f.startswith("processed_chunk_") and f.endswith(".png")
        ]
        if len(processed) == num_chunks:
            print("[MASTER] All chunks processed.", flush=True)
            break
        sleep(1)

def combine_chunks(num_chunks, output_path, chunk_dir):
    print("[MASTER] Combining chunks into final output...", flush=True)
    chunks = []
    for i in range(num_chunks):
        chunk_path = os.path.join(chunk_dir, f"processed_chunk_{i}.png")
        img = Image.open(chunk_path)
        chunks.append(img)
        os.remove(chunk_path)

    total_height = sum(chunk.size[1] for chunk in chunks)
    width = chunks[0].size[0]

    final_image = Image.new("RGB", (width, total_height))
    y_offset = 0
    for chunk in chunks:
        final_image.paste(chunk, (0, y_offset))
        y_offset += chunk.size[1]

    final_image.save(output_path)
    print(f"[MASTER] Final image saved to {output_path}", flush=True)

def main():
    print("[MASTER] Starting master pipeline...",flush=True)
    
    while True:
        for filename in os.listdir(INPUT_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(INPUT_DIR, filename)
                 # Step 1: Split the image
                split_image(file_path, N_WORKERS, CHUNKS_DIR)
                
                # Step 2: Launch workers
                for i in range(N_WORKERS):
                    launch_worker(i)
                
                # Step 3: Wait for results
                wait_for_processed_chunks(N_WORKERS, CHUNKS_DIR)

                # Step 4: Combine processed results
                output_filename = f"processed_{os.path.splitext(filename)[0]}.png"
                output_file = os.path.join(OUTPUT_DIR, output_filename)
                combine_chunks(N_WORKERS, output_file, CHUNKS_DIR)
                print("[MASTER] All done!", flush=True)
                os.remove(file_path)
                print(f"[MASTER] Deleted input file {file_path}", flush=True)
                delete_on_bucket(filename)

if __name__ == "__main__":
    main()
