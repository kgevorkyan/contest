from xml.etree import ElementTree
import argparse
import json
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from modules.parsers.result_parser import ResultParser
from modules.parsers.source_parser import SourceParser
from modules.evaluator import Evaluator


def check_args(arg_parser: argparse.ArgumentParser, args: argparse.Namespace):
    if not os.path.isdir(args.tests_dir):
        arg_parser.error(f"Tests directory doesn't exist: {args.tests_dir}")

    if not os.path.isdir(args.tools_results):
        arg_parser.error(f"Tools results directory doesn't exist: {args.tools_results}")

    if not os.path.isfile(args.true_reports):
        arg_parser.error(f"True results file doesn't exist: {args.true_reports}")


def parse_args(arg_list: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluator for static analysis tools")
    parser.add_argument("--tests", dest="tests_dir",
                        help="Tests directory path", required=True)
    parser.add_argument("--tools-results", dest="tools_results",
                        help="The directory path where the all tools were running", required=True)
    parser.add_argument("--true-reports", dest="true_reports",
                        help="Path to correct results of tests", required=True)
    parser.add_argument("--inner-res-name", dest="inner_res_name",
                        help="Inner directory name where are stored reports of each tool",
                        default="result_sarif_files")
    args = parser.parse_args(arg_list)
    check_args(parser, args)
    return args


def evaluate_and_get_scores(all_res_path: str, true_reports_path: str,
                            src_dir: str, inner_res_name: str) -> dict:
    scores = {}
    source_parser = SourceParser(src_dir)
    src_functions = source_parser.functions()

    true_reports_parser = ResultParser(res_path=true_reports_path)
    true_reports = true_reports_parser.get_all_reports()

    for item in os.listdir(all_res_path):
        try:
            item = os.path.join(all_res_path, item, inner_res_name)
            if not os.path.isdir(item):
                continue

            received_results_parser = ResultParser(item)

            received_reports = received_results_parser.get_all_reports()
            evaluator = Evaluator(true_reports=true_reports, received_reports=received_reports,
                                  src_functions=src_functions)

            scores[received_results_parser.tool_name()] = evaluator.average_score()

        except (ValueError, FileNotFoundError) as error:
            print(type(error).__name__, ": ", error)

    return scores


def create_output_files(scores: dict) -> None:
    tools = ElementTree.Element("scores")

    for tool_name, score in scores.items():
        entry = ElementTree.SubElement(tools, "entry")
        tool_name_el = ElementTree.SubElement(entry, "tool_name")
        score_el = ElementTree.SubElement(entry, "score")
        tool_name_el.text = tool_name
        score_el.text = str(score)

    tree = ElementTree.ElementTree(tools)
    tree.write("scores.xml")
    with open("scores.json", 'w') as scores_file:
        json.dump(scores, scores_file, indent=4)


def main(arg_list: list):
    args = parse_args(arg_list)
    scores = evaluate_and_get_scores(
        args.tools_results, args.true_reports, args.tests_dir, args.inner_res_name)
    create_output_files(scores)


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as err:
        print(type(err).__name__, ": ", err)
        exit(1)
