import os
import argparse
import sys

from .. import guess_host, config
from ..experiment import XPmaker
from ..util import expandpath

__all__ = ["new_xp"]

DAVAI_HOST = guess_host()


def get_parser():
    parser = argparse.ArgumentParser(
        description="Create a Davai experiment based on a Git reference."
    )
    parser.add_argument("IAL_git_ref", help="IFS-Arpege-LAM Git reference to be tested")
    repos = parser.add_mutually_exclusive_group()
    repos.add_argument(
        "--IAL_repo",
        default=expandpath(config["paths"]["IAL_repository"]),
        dest="IAL_repository",
        help="Path to IFS-Arpege-LAM Git repository in which to find 'IAL_git_ref' argument. "
        + (
            "Default ({}) can be set through section [paths] " + "of user config file"
        ).format(config["paths"]["IAL_repository"]),
    )
    parser.add_argument(
        "-v",
        "--tests_version",
        dest="davai_tests_version",
        help="Version of the Davai test bench to be used.",
        required=True,
    )
    parser.add_argument(
        "-c",
        "--comment",
        default=None,
        help="Comment about experiment. Defaults to IAL_git_ref, IAL_bundle or IAL_bundle_file.",
    )
    parser.add_argument(
        "-u",
        "--usecase",
        default=config["defaults"]["usecase"],
        help="Usecase: NRV (restrained set of canonical tests) or ELP (extended elementary tests); "
        + "More (PC, ...) to come. Defaults to: '{}'".format(
            config["defaults"]["usecase"]
        ),
    )
    parser.add_argument(
        "--origin",
        "--davai_tests_origin",
        default=config["defaults"]["davai_tests_origin"],
        dest="davai_tests_origin",
        help=(
            "URL of the DAVAI-tests origin repository to be cloned in XP. "
            + "Default ({}) can be set through section [defaults] "
            + "of user config file"
        ).format(config["defaults"]["davai_tests_origin"]),
    )
    parser.add_argument(
        "--host",
        default=DAVAI_HOST,
        help="Generic name of host machine, in order to find paths to necessary packages. "
        + (
            "Default is guessed ({}), or can be set through "
            + "section 'hosts' of user config file"
        ).format(DAVAI_HOST),
    )
    return parser


def new_xp():
    """
    Setup an XP.

    :param sources_to_test: information about the sources to be tested, provided as a dict
    :param davai_tests_version: version of the test bench to be used
    :param davai_tests_origin: URL of the DAVAI-tests origin repository to be cloned in XP
    :param usecase: among NRV, ELP, PC, ...
    :param host: name of host machine, to link necessary packages and get according config file
        (otherwise guessed)
    """

    args = get_parser().parse_args()

    if "IAL_git_ref" in args:
        sources_to_test = dict(
            IAL_git_ref=args.IAL_git_ref,
            IAL_repository=os.path.abspath(args.IAL_repository),
        )
    elif "IAL_bundle" in args:
        sources_to_test = dict(
            IAL_bundle=args.IAL_bundle,
            IAL_bundle_repository=os.path.abspath(args.IAL_bundle_repository),
        )
    elif "IAL_bundle_file" in args:
        sources_to_test = dict(IAL_bundle_file=os.path.abspath(args.IAL_bundle_file))
    sources_to_test["comment"] = args.comment

    xp = XPmaker.new_xp(
        sources_to_test=sources_to_test,
        davai_tests_version=args.davai_tests_version,
        davai_tests_origin=args.davai_tests_origin,
        usecase=args.usecase,
        host=args.host,
    )
    xp.write_genesis(" ".join(sys.argv))
