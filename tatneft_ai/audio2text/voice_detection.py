import time
import whisper
import torch

def whisper_audio2text(target_file_name, name_file="result.txt", debug=False):
    text_with_time = []
    text_dict = []

    time_start = time.time()
    if torch.cuda.is_available():
        print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
        model = whisper.load_model("tiny", device="cuda")
    else:
        print("CUDA is not available. Using CPU.")
        model = whisper.load_model("tiny")

    result = model.transcribe(target_file_name)
    time_end = time.time()
    if debug:
        print(f"Time: {time_end-time_start}")
        print(result["text"])
        print(result)

    for segment in result["segments"]:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"]
        text_with_time.append(f"[{start_time:.2f} - {end_time:.2f}] {text}")
        # text_dict.append({
        #     "start_time": start_time,
        #     "end_time": end_time,
        #     "text": text,
        # })

    with open(name_file, "w") as file:
        file.write(str(text_with_time))

    # return text_with_time
    return result["segments"]


if __name__ == "__main__":
    whisper_audio2text()