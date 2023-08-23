from typing import Optional
import clang.cindex as cl
import queue
import os


class Function:
    def __init__(self, name: str, start_line: int, end_line: int, file_path: str) -> None:
        self.__name = name
        self.__start_line = start_line
        self.__end_line = end_line
        self.__file_path = file_path
        self.__source_name = SourceParser.get_source_name(self.__file_path)

    def name(self) -> str:
        return self.__name

    def start_line(self) -> int:
        return self.__start_line

    def end_line(self) -> int:
        return self.__end_line

    def file_path(self) -> str:
        return self.__file_path

    @staticmethod
    def get_dict_by_source_name(functions: list) -> dict:
        functions_dict = {}
        for function in functions:
            if function.__source_name not in functions_dict:
                functions_dict[function.__source_name] = []

            functions_dict[function.__source_name].append(function)

        return functions_dict

    def __eq__(self, other) -> bool:
        return (isinstance(other, Function)
                and self.__name == other.__name
                and self.__start_line == other.__start_line
                and self.__end_line == other.__end_line
                and SourceParser.is_same_path(self.__file_path, other.__file_path))


class SourceParser:
    def __init__(self, src_dir: str) -> None:
        cl.Config.set_library_file("libclang-12.so")
        self.__src_dir = os.path.realpath(src_dir)
        self.__functions = []
        self.__info_collected = False

    @staticmethod
    def get_parent_function(src_functions: list, file_path: str, line: int) -> Optional[Function]:
        for function in src_functions:
            if (SourceParser.is_same_path(function.file_path(), file_path) and
                    function.start_line() <= line <= function.end_line()):
                return function

        return None

    @staticmethod
    def is_same_path(path_1: str, path_2: str) -> bool:
        return path_1.endswith(path_2) or path_2.endswith(path_1)

    @staticmethod
    def add_in_list(function: Optional[Function], src_functions: list) -> None:
        if function and function not in src_functions:
            src_functions.append(function)

    @staticmethod
    def get_path_from_uri(uri: str) -> str:
        uri_prefix = "file://"
        if uri.startswith(uri_prefix):
            return uri[len(uri_prefix):]

        return uri

    @staticmethod
    def get_num_from_dict(file_to_functions: dict) -> int:
        num = 0
        for file, functions in file_to_functions.items():
            num += len(functions)

        return num

    def number_of_functions(self) -> int:
        self.__collect_information()
        return len(self.__functions)

    def functions(self) -> list:
        self.__collect_information()
        return self.__functions

    def __collect_information(self) -> None:
        if self.__info_collected:
            return

        dir_queue = queue.Queue()
        dir_queue.put(self.__src_dir)

        cl_index = cl.Index.create()
        while not dir_queue.empty():
            tmp_dir = dir_queue.get()
            for tmp_file in os.listdir(tmp_dir):
                file_real_p = os.path.join(tmp_dir, tmp_file)
                if os.path.isdir(file_real_p):
                    dir_queue.put(file_real_p)
                    continue

                if self.__is_c_file(file_real_p):
                    cl_tu = cl_index.parse(file_real_p)
                    for function in self.__extract_functions(cl_tu.cursor):
                        SourceParser.add_in_list(function=function, src_functions=self.__functions)

        self.__info_collected = True

    @staticmethod
    def __extract_functions(cl_cursor: cl.TranslationUnit) -> list:
        cursor_queue = queue.Queue()
        cursor_queue.put(cl_cursor)

        functions = []
        while not cursor_queue.empty():
            tmp_cursor = cursor_queue.get()
            if tmp_cursor.kind == cl.CursorKind.FUNCTION_DECL and tmp_cursor.is_definition():
                extent = tmp_cursor.extent
                functions.append(
                    Function(name=tmp_cursor.spelling, start_line=extent.start.line,
                             end_line=extent.end.line, file_path=extent.start.file.name))

            else:
                for child in tmp_cursor.get_children():
                    cursor_queue.put(child)

        return functions

    @staticmethod
    def __is_c_file(file_path):
        return file_path.endswith(".c") or file_path.endswith(".h")

    @staticmethod
    def get_source_name(uri: str) -> str:
        dir_path_1 = os.path.dirname(uri)
        dir_path_2 = os.path.dirname(dir_path_1)
        dir_name = os.path.basename(dir_path_1)
        return os.path.basename(dir_path_2) + "_" + dir_name.split('_')[0]
