import json
import os
import requests
import time


API_URL = "https://tela33amek.vercel.app/api/upload-paper/"



def upload_paper(paper):
    path = paper["path"]

    if not os.path.isfile(path):
        print(f"[SKIP] File not found: {path}")
        return False

    filename = os.path.basename(path)

    print(f"[UPLOAD] {filename}")

    data = {
        "course": paper["course"],
        "major": paper["major"],
        "year": paper["year"],
        "semester": paper["semester"],
        "level": paper["level"],
        "establishment": paper["establishment"],
        "teacher": paper["teacher"],
        "paper_type": paper["paper_type"],
        "session": paper["session"],
    }

    try:
        with open(path, "rb") as f:

            files = {
                "file": (
                    filename,
                    f,
                    "application/pdf"
                )
            }

            response = requests.post(
                API_URL,
                data=data,
                files=files,
                timeout=120
            )

        if response.status_code == 201:
            result = response.json()

            print(
                f"[SUCCESS] {filename} "
                f"(ID: {result.get('id')})"
            )

            return True

        else:
            print(
                f"[ERROR] {filename}\n"
                f"Status: {response.status_code}\n"
                f"Response: {response.text}"
            )

            return False

    except requests.RequestException as e:
        print(f"[NETWORK ERROR] {filename}: {e}")
        return False


def main():
    json_file = input("enter the json path:")
    with open(json_file, "r", encoding="utf-8") as f:
        papers = json.load(f)

    print(f"Found {len(papers)} files.\n")

    successful = 0
    failed = 0

    for i, paper in enumerate(papers, 1):

        print(f"[{i}/{len(papers)}]")

        if upload_paper(paper):
            successful += 1
        else:
            failed += 1

        # Small delay between uploads
        time.sleep(0.2)

    print("\n====================")
    print("UPLOAD COMPLETE")
    print("====================")
    print(f"Successful: {successful}")
    print(f"Failed:     {failed}")
    print(f"Total:      {len(papers)}")


if __name__ == "__main__":
    main()