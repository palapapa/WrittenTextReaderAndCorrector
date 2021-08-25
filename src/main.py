import cv2
import PIL.Image
import argparse
import symspellpy
import pytesseract
import os
import pkg_resources
import numpy

def load_images(paths: list[str]) -> tuple[list[PIL.Image.Image], list[str]]:
    images: list[PIL.Image.Image] = list()
    image_paths: list[str] = list()
    for path in paths:
        if os.path.isdir(path):
            files: list[str]
            if os.path.isabs(path):
                files = [file for file in os.listdir(path) if not os.path.isdir(file)]
            else:
                files = [os.path.abspath(os.path.join(path, file)) for file in os.listdir(path) if not os.path.isdir(file)]
            for file in files:
                try:
                    images.append(PIL.Image.open(file))
                except Exception as e:
                    print(f"{file} cannot be opened.({str(e)})")
            image_paths.extend(files)
        else:
            images.append(PIL.Image.open(path))
            image_paths.append(path)
    return images, image_paths

def main() -> None:
    argument_parser: argparse.ArgumentParser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "-i",
        "--in",
        action="append",
        required=True,
        metavar="paths",
        help="Paths to the images to be scanned.",
        type=str,
        dest="input_paths"
    )
    argument_parser.add_argument(
        "-o",
        "--out",
        action="store",
        nargs=1,
        required=True,
        metavar="path",
        help="Path to the output file. A new file will be created if the provided path does not exist.",
        type=str,
        dest="output_path"
    )
    argument_parser.add_argument(
        "-n",
        "--no-auto-correct",
        action="store_false",
        required=False,
        help="Whether to disable auto-correct.",
        default=True,
        dest="auto_correct"
    )
    arguments: argparse.Namespace = argument_parser.parse_args()
    images: list[PIL.Image.Image]
    image_paths: list[str]
    (images, image_paths) = load_images(arguments.input_paths)
    for image in images:
        image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2GRAY)
    result: str = str()
    before_auto_correct: list[str] = list()
    after_auto_correct: list[list[symspellpy.symspellpy.SuggestItem]] = list(list())
    symspell: symspellpy.SymSpell = symspellpy.SymSpell()
    bigram_path: str = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")
    symspell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    for i in range(len(images)):
        try:
            before_auto_correct.append(str(pytesseract.image_to_string(images[i])))
        except Exception as e:
            print(f"{image_paths[i]} cannot be opened.({str(e)})")
    if arguments.auto_correct:
        def auto_correct() -> None:
            for before in before_auto_correct:
                suggestion: list[symspellpy.symspellpy.SuggestItem] = symspell.lookup_compound(before, max_edit_distance=2, transfer_casing=True)
                after_auto_correct.append(suggestion)
        auto_correct() # Python why are you like this?????? Why can't a loop have its own scope?????
        for suggestions in after_auto_correct:
            paragraph: str = str()
            for suggestion in suggestions:
                paragraph += suggestion.term + " "
            paragraph = paragraph.strip()
            result += paragraph + "\n"
    else:
        result = "\n".join(before_auto_correct)
    try:
        with open(arguments.output_path[0], "a+") as output:
            output.write(result)
    except EnvironmentError as e:
        print(f"FAILED: The output file cannot be written to.({str(e)})")
        

if __name__ == "__main__":
    main()