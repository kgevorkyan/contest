import queue
import sys
import os
from pysarif import load_from_file

sys.path.append(os.path.join(os.path.dirname(__file__)))

from source_parser import SourceParser


class Location:
    def __init__(self, uri: str, start_line: int) -> None:
        self.__uri = uri
        self.__start_line = start_line

    def uri(self) -> str:
        return self.__uri

    def start_line(self) -> int:
        return self.__start_line

    def __eq__(self, other) -> bool:
        return (isinstance(other, Location)
                and SourceParser.is_same_path(self.__uri, other.__uri)
                and self.__start_line == other.__start_line)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)


class Report:
    def __init__(self, report_type: str, locations: list, trace: list) -> None:
        self.__report_type = report_type
        self.__locations = locations
        self.__trace = trace
        self.__source_name = self.__get_source_name()

    def locations(self) -> list:
        return self.__locations

    def trace(self) -> list:
        return self.__trace

    @staticmethod
    def get_dict_by_source_name(reports: list) -> dict:
        reports_dict = {}
        for report in reports:
            if report.__source_name not in reports_dict:
                reports_dict[report.__source_name] = []

            reports_dict[report.__source_name].append(report)

        return reports_dict

    def __eq__(self, other) -> bool:
        return (isinstance(other, Report) and self.__report_type == other.__report_type
                and self.__are_equal_lists(self.__locations, other.__locations)
                and self.__are_equal_lists(self.__trace, other.__trace))

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self):
        return f"Report: type='{self.__report_type}', location={self.__locations.__str__()}, \
            trace={self.__trace.__str__()}"

    def __get_source_name(self) -> str:
        source_name = ""
        for location in self.__locations:
            return SourceParser.get_source_name(location.uri())

        return source_name

    @staticmethod
    def __are_equal_lists(l1: list, l2: list) -> bool:
        if len(l1) != len(l2):
            return False

        for i in range(0, len(l1)):
            if l1[i] != l2[i]:
                return False

        return True


class ResultParser:
    def __init__(self, res_path: str) -> None:
        self.__res_path = res_path

        self.__parsing_done = False
        self.__reports = {}
        self.__tool_name = ""
        self.__def_tool_name = self.__default_tool_name()

    def tool_name(self) -> str:
        self.__parse_results()

        if self.__tool_name == "":
            return self.__def_tool_name

        return self.__tool_name

    def get_reports_by_report_type(self, report_type: str) -> list:
        self.__parse_results()
        return self.__reports[report_type]

    def get_all_reports(self) -> list:
        self.__parse_results()
        reports_list = []
        for report_type, reports in self.__reports.items():
            for report in reports:
                reports_list.append(report)

        return reports_list

    def __parse_results(self) -> None:
        if self.__parsing_done:
            return

        self.__res_path = os.path.realpath(self.__res_path)
        if os.path.isdir(self.__res_path):
            self.__parse_results_recursive()
        else:
            self.__parse_single_result(self.__res_path)

        self.__parsing_done = True

    def __parse_rules(self, tool_rules: list) -> None:
        for rule in tool_rules:
            if rule.id not in self.__reports:
                self.__reports[rule.id] = []

    def __parse_results_recursive(self) -> None:
        dir_queue = queue.Queue()
        dir_queue.put(self.__res_path)

        while not dir_queue.empty():
            tmp_dir = dir_queue.get()
            for tmp_file in os.listdir(tmp_dir):
                file_real_p = os.path.join(tmp_dir, tmp_file)
                if os.path.isdir(file_real_p):
                    dir_queue.put(file_real_p)
                else:
                    self.__parse_single_result(file_real_p)

    def __parse_single_result(self, path_to: str) -> None:
        if not path_to.endswith(".sarif"):
            return

        report = load_from_file(path_to)
        for run in report.runs:
            self.__parse_rules(run.tool.driver.rules)
            self.__update_tool_name(run.tool.driver.name)
            for report in run.results:
                ResultParser.add_in_list(
                    report=Report(report_type=report.rule_id,
                                  locations=ResultParser.__get_locations(report.locations),
                                  trace=ResultParser.__get_trace(report.code_flows)),
                    reports=self.__reports[report.rule_id])

    def __update_tool_name(self, new_name: str) -> None:
        if self.__tool_name != "" and self.__tool_name != new_name:
            raise RuntimeError("Result directory must contain reports generated only by one tool.")

        self.__tool_name = new_name

    def __default_tool_name(self) -> str:
        return os.path.basename(os.path.dirname(self.__res_path))

    @staticmethod
    def add_in_list(report: Report, reports: list) -> None:
        for tmp_report in reports:
            if tmp_report == report:
                return

        reports.append(report)

    @staticmethod
    def __get_locations(locations: list) -> list:
        locations_list = []
        for location in locations:
            locations_list.append(ResultParser.__get_location(location))

        return locations_list

    @staticmethod
    def __get_trace(code_flows: list) -> list:
        locations_list = []
        for code_flow in code_flows:
            for thread_flow in code_flow.thread_flows:
                for location in thread_flow.locations:
                    locations_list.append(ResultParser.__get_location(location.location))

        return locations_list

    @staticmethod
    def __get_location(location: any) -> Location:
        tmp = location.physical_location
        region = tmp.region
        return Location(uri=tmp.artifact_location.uri, start_line=region.start_line)
