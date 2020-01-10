import pytest

from naomi_bot import version

def test_get_version_number():
  description_text = """
  Package: naomi
  Title: Naomi model for subnational HIV estimates
  Version: 0.0.49
  Authors@R:

  """
  assert version.get_version_number(description_text) == "0.0.49"

  # Missing version
  with pytest.raises(Exception):
    version.get_version_number("test")

  description_text = """
  Package: aoc
  Title: Advent of code with Rcpp
  Version: 0.0.2 
  Authors@R: 
      person(given = "Robert",
             family = "Ashton",
             role = c("aut", "cre"),
             email = "r.ashton@imperial.ac.uk")
  Description: Solves Advent of Code puzzles using Rcpp
  License: MIT + file LICENSE
  Encoding: UTF-8
  LazyData: true
  Suggests: 
      testthat
  Roxygen: list(markdown = TRUE)
  RoxygenNote: 6.1.1
  LinkingTo: 
      Rcpp
  Imports: 
      Rcpp
  """
  assert version.get_version_number(description_text) == "0.0.2"

def test_update_naomi_version():
  description_text = """
  Package: naomi
  Title: Naomi model for subnational HIV estimates
  Version: 0.0.49
  Authors@R:
  Imports:
      digest,
      docopt,
      geojsonio (>= 0.8.0),
      naomi (>= 0.0.48),
      plumber
  """
  assert version.update_naomi_version(description_text, "0.0.49") == """
  Package: naomi
  Title: Naomi model for subnational HIV estimates
  Version: 0.0.49
  Authors@R:
  Imports:
      digest,
      docopt,
      geojsonio (>= 0.8.0),
      naomi (>= 0.0.49),
      plumber
  """

  # Failed to update version
  with pytest.raises(Exception):
    version.update_naomi_version(description_text, "0.0.48")

def test_update_travis():
  travis_text = """
  language: R
  sudo: false
  r_github_packages:
    - ropensci/jsonvalidate
    - mrc-ide/naomi
    - mrc-ide/rrq
  """
  assert version.update_travis(travis_text, "new-branch") == """
  language: R
  sudo: false
  r_github_packages:
    - ropensci/jsonvalidate
    - mrc-ide/naomi@new-branch
    - mrc-ide/rrq
  """

  # Failed to update version
  with pytest.raises(Exception):
    version.update_travis("""
      language: R
      sudo: false
      r_github_packages:
        - ropensci/jsonvalidate
        - mrc-ide/naomi@new-branch
        - mrc-ide/rrq
    """, "new_branch")

def test_update_docker_build():
  docker_text = """
  set -e
  HERE=$(dirname $0)
  . $HERE/common

  git clone https://github.com/mrc-ide/naomi

  docker build --pull .
  """

  assert version.update_docker_build(docker_text, "new-branch") == """
  set -e
  HERE=$(dirname $0)
  . $HERE/common

  git clone --single-branch --branch new-branch https://github.com/mrc-ide/naomi

  docker build --pull .
  """

  with pytest.raises(Exception):
    version.update_docker_build("""
    set -e
    HERE=$(dirname $0)
    . $HERE/common

    git clone --single-branch --branch other-branch https://github.com/mrc-ide/naomi

    docker build --pull .
    """, "new-branch")