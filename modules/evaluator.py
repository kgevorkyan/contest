from parsers.source_parser import SourceParser
from parsers.source_parser import Function
from parsers.result_parser import Report


class Accuracy:
    def __init__(self, true_reports_num: int, received_reports_num: int,
                 bad_functions_num: int, good_functions_num: int) -> None:
        self.__tp_num = true_reports_num
        self.__fp_num = received_reports_num - self.__tp_num
        self.__tn_num = good_functions_num - self.__fp_num
        self.__fn_num = bad_functions_num - self.__tp_num
        self.__set_zero_if_neg()

    def true_positive_num(self) -> int:
        return self.__tp_num

    def false_positive_num(self) -> int:
        return self.__fp_num

    def true_negative_num(self) -> int:
        return self.__tn_num

    def false_negative_num(self) -> int:
        return self.__fn_num

    def true_positive_rate(self) -> float:
        return 100 * self.__tp_num / (self.__tp_num + self.__fn_num)

    def false_positive_rate(self) -> float:
        return 100 * self.__fp_num / (self.__fp_num + self.__tn_num)

    def true_negative_rate(self) -> float:
        return 100 * self.__tn_num / (self.__tn_num + self.__fp_num)

    def false_negative_rate(self) -> float:
        return 100 * self.__fn_num / (self.__fn_num + self.__tp_num)

    def f1_score(self) -> float:
        return self.__tp_num / (self.__tp_num + (self.__fp_num + self.__fn_num) / 2)

    def __set_zero_if_neg(self) -> None:
        if self.__tp_num < 0:
            self.__tp_num = 0
        if self.__tn_num < 0:
            self._tn_count = 0
        if self.__fp_num < 0:
            self.__fp_num = 0
        if self.__fn_num < 0:
            self.__fn_num = 0


# we expect that in sources each function may contain only less than one error
class Evaluator:
    def __init__(self, true_reports: list, received_reports: list,
                 src_functions: list) -> None:
        self.__true_reports = true_reports
        self.__received_reports = received_reports
        self.__src_functions = src_functions
        self.__bad_functions = []
        self.__good_functions = []

        self.__evaluated = False
        self.__accuracy = None
        self.__average_score = -1

    def accuracy(self) -> Accuracy:
        self.__evaluate()
        return self.__accuracy

    def average_score(self) -> float:
        self.__evaluate()
        self.__evaluate_average_score()
        return self.__average_score

    @staticmethod
    def get_intersection(first: list, second: list) -> list:
        intersection = []
        for cur_el in first:
            if cur_el in second:
                intersection.append(cur_el)

        return intersection

    def __evaluate(self) -> None:
        if self.__evaluated:
            return

        self.__tp_results = Evaluator.get_intersection(self.__true_reports, self.__received_reports)
        self.__collect_bad_functions()
        self.__collect_good_functions()
        self.__accuracy = Accuracy(true_reports_num=len(self.__tp_results),
                                   received_reports_num=len(self.__received_reports),
                                   bad_functions_num=len(self.__bad_functions),
                                   good_functions_num=len(self.__good_functions))

        self.__evaluated = True

    def __collect_bad_functions(self) -> None:
        for report in self.__true_reports:
            for location in report.locations():
                file_path = SourceParser.get_path_from_uri(location.uri())
                function = SourceParser.get_parent_function(
                    src_functions=self.__src_functions, file_path=file_path,
                    line=location.start_line())

                SourceParser.add_in_list(function=function, src_functions=self.__bad_functions)

    def __collect_good_functions(self) -> None:
        for function in self.__src_functions:
            if function not in self.__bad_functions:
                SourceParser.add_in_list(function=function, src_functions=self.__good_functions)

    def __evaluate_average_score(self) -> None:
        if self.__average_score != -1:
            return

        src_to_true = Report.get_dict_by_source_name(self.__true_reports)
        src_to_received = Report.get_dict_by_source_name(self.__received_reports)
        src_to_bad = Function.get_dict_by_source_name(self.__bad_functions)
        src_to_good = Function.get_dict_by_source_name(self.__good_functions)
        self.__average_score = 0

        for src_name, true_reports in src_to_true.items():
            received_reports = src_to_received[src_name] if src_name in src_to_received else []

            true_rep_num = len(Evaluator.get_intersection(true_reports, received_reports))
            bad_func_num = len(src_to_bad[src_name]) if src_name in src_to_bad else 0
            good_func_num = len(src_to_good[src_name]) if src_name in src_to_good else 0
            tmp_accuracy = (
                Accuracy(true_reports_num=true_rep_num, received_reports_num=len(received_reports),
                         bad_functions_num=bad_func_num, good_functions_num=good_func_num))

            tmp_score = tmp_accuracy.f1_score() * Evaluator.__get_coefficient(src_name)
            self.__average_score += tmp_score

    @staticmethod
    def __get_coefficient(src_name: str) -> int:
        coefficient_dict = {"EASY": 1, "MEDIUM": 2, "HARD": 3}
        key_val = (src_name.split('_')[-1]).split('0')[0]
        if key_val in coefficient_dict:
            return coefficient_dict[key_val]

        return 1
