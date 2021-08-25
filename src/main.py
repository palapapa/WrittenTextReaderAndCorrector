import cv2
import PIL.Image
import argparse
import symspellpy
import pytesseract
import os
import pkg_resources

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
        nargs="?",
        required=True,
        metavar="path",
        help="Path to the output file. A new directory will be created if the provided path does not exist.",
        type=str,
        dest="output_path"
    )
    argument_parser.add_argument(
        "-a",
        "--auto-correct",
        action="store_true",
        required=False,
        help="Whether to use auto-correct.",
        default=False,
        dest="auto_correct"
    )
    arguments: argparse.Namespace = argument_parser.parse_args()
    images: list[PIL.Image.Image]
    image_paths: list[str]
    (images, image_paths) = load_images(arguments.input_paths)
    result: str = str()
    before_auto_correct: list[list[str]] = list(list())
    after_auto_correct: list[list[symspellpy.symspellpy.SuggestItem]] = list(list())
    symspell: symspellpy.SymSpell = symspellpy.SymSpell()
    dictionary_path: str = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
    bigram_path: str = pkg_resources.resource_filename("symspellpy", "frequency_bigramdictionary_en_243_342.txt")
    symspell.load_dictionary(dictionary_path, term_index=0, count_index=1)
    symspell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    for i in range(len(images)):
        try:
            before_auto_correct.append(str(pytesseract.image_to_string(images[i])).split(" "))
        except Exception as e:
            print(f"{image_paths[i]} cannot be opened.({str(e)})")
    if arguments.auto_correct:
        def auto_correct() -> None:
            for paragraph in before_auto_correct:
                corrected_paragraph: list[symspellpy.symspellpy.SuggestItem] = list()
                for word in paragraph:
                    try:
                        corrected_paragraph.append(symspell.lookup(word, symspellpy.symspellpy.Verbosity.TOP)[0])
                    except:
                        corrected_paragraph.append(symspellpy.symspellpy.SuggestItem(word, None, None))
                after_auto_correct.append(corrected_paragraph)
        auto_correct() # Python why are you like this?????? Why can't a loop have its own scope?????
        for paragraph_suggestion in after_auto_correct:
            for word_suggestion in paragraph_suggestion:
                result += word_suggestion.term + " "
            result += "\n"
    else:
        for paragraph in before_auto_correct:
            for word in paragraph:
                result += word + " "
            result += "\n"
    try:
        with open(arguments.output_path, "a+") as output:
            output.write(result)
    except EnvironmentError as e:
        print(f"FAILED: The output file cannot be written to.({str(e)})")
        

if __name__ == "__main__":
    main()