"""Tests for Markdown link and image extractor."""

from deadlinkfinder.extractor import extract_links_from_text


def test_extracts_markdown_links() -> None:
    doc = """
Check out the [Documentation](./docs/readme.md) and [License](LICENSE).
Also see [Website](https://example.com).
"""
    refs = extract_links_from_text(doc)
    assert len(refs) == 3

    local_doc = refs[0]
    assert local_doc.display_text == "Documentation"
    assert local_doc.target_path == "./docs/readme.md"
    assert local_doc.is_external is False
    assert local_doc.is_image is False

    license_ref = refs[1]
    assert license_ref.target_path == "LICENSE"
    assert license_ref.is_external is False

    ext_ref = refs[2]
    assert ext_ref.is_external is True


def test_extracts_images() -> None:
    doc = "![Banner](assets/banner.png)\n"
    refs = extract_links_from_text(doc)
    assert len(refs) == 1
    assert refs[0].is_image is True
    assert refs[0].target_path == "assets/banner.png"


def test_extracts_anchor_links() -> None:
    doc = "[Jump to setup](#setup)\n[Cross doc anchor](other.md#section-one)"
    refs = extract_links_from_text(doc)
    assert len(refs) == 2
    assert refs[0].target_path == ""
    assert refs[0].anchor == "setup"

    assert refs[1].target_path == "other.md"
    assert refs[1].anchor == "section-one"


def test_ignores_links_in_code_blocks() -> None:
    doc = """
[Real Link](real.md)

```bash
# Code block:
curl -s http://ignore-me.com/api
[Fake Link](fake.md)
```

And inline code `[Also Fake](ignore.md)` is ignored.
"""
    refs = extract_links_from_text(doc)
    assert len(refs) == 1
    assert refs[0].target_path == "real.md"


def test_extracts_rst_inline_links() -> None:
    doc = """
Check out the `Documentation <./docs/readme.rst>`_ and `License <LICENSE>`_.
Also see `Website <https://example.com>`_ and `Anonymous <https://other.org>`__.
"""
    refs = extract_links_from_text(doc, source_file="index.rst")
    assert len(refs) == 4

    local_doc = refs[0]
    assert local_doc.display_text == "Documentation"
    assert local_doc.target_path == "./docs/readme.rst"
    assert local_doc.is_external is False
    assert local_doc.is_image is False

    license_ref = refs[1]
    assert license_ref.target_path == "LICENSE"
    assert license_ref.is_external is False

    ext_ref = refs[2]
    assert ext_ref.is_external is True
    assert ext_ref.target_path == "https://example.com"

    anon_ref = refs[3]
    assert anon_ref.is_external is True
    assert anon_ref.target_path == "https://other.org"


def test_extracts_rst_images_and_figures() -> None:
    doc = """
.. image:: assets/banner.png
   :alt: Project Banner
   :width: 400px

.. figure:: _static/architecture.svg
   :alt: Architecture Diagram
"""
    refs = extract_links_from_text(doc, source_file="index.rst")
    assert len(refs) == 2

    assert refs[0].is_image is True
    assert refs[0].target_path == "assets/banner.png"

    assert refs[1].is_image is True
    assert refs[1].target_path == "_static/architecture.svg"


def test_extracts_rst_target_links() -> None:
    doc = """
.. _Python: https://www.python.org
.. _Installation: ./docs/install.rst
"""
    refs = extract_links_from_text(doc, source_file="index.rst")
    assert len(refs) == 2

    assert refs[0].display_text == "Python"
    assert refs[0].target_path == "https://www.python.org"
    assert refs[0].is_external is True

    assert refs[1].display_text == "Installation"
    assert refs[1].target_path == "./docs/install.rst"
    assert refs[1].is_external is False


def test_extracts_rst_roles() -> None:
    doc = """
See :doc:`installation` and :doc:`Quick Setup <./setup.rst>`.
Also refer to :ref:`prerequisites` and :download:`Config Script <scripts/setup.py>`.
"""
    refs = extract_links_from_text(doc, source_file="index.rst")
    assert len(refs) == 4

    assert refs[0].target_path == "installation"
    assert refs[1].target_path == "./setup.rst"
    assert refs[1].display_text == "Quick Setup"

    assert refs[2].anchor == "prerequisites"
    assert refs[2].target_path == ""

    assert refs[3].target_path == "scripts/setup.py"


def test_extracts_rst_anchor_links() -> None:
    doc = """
`Jump to setup <#setup>`_
`Cross doc anchor <other.rst#section-one>`_
"""
    refs = extract_links_from_text(doc, source_file="index.rst")
    assert len(refs) == 2

    assert refs[0].target_path == ""
    assert refs[0].anchor == "setup"

    assert refs[1].target_path == "other.rst"
    assert refs[1].anchor == "section-one"


def test_ignores_rst_code_blocks_and_inline_code() -> None:
    doc = """
`Real Link <real.rst>`_

.. code-block:: python

    # Inside code block:
    url = "http://ignore-me.com"
    `Fake Link <fake.rst>`_

And inline literal `` `Also Fake <ignore.rst>`_ `` is ignored.
"""
    refs = extract_links_from_text(doc, source_file="index.rst")
    assert len(refs) == 1
    assert refs[0].target_path == "real.rst"
