import logging
import os
import sys
import pickle

from flaskr.database import *
import flaskr.configuration

logging.basicConfig(stream=sys.stdout)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def flatten(l):
    """
    helper function
    """
    return [item for sublist in l for item in sublist]


def get_tags():
    """
    Get dictionary of tags
    """
    tags = None
    with open(flaskr.configuration.TAGS) as f:
        tags = f.readlines()
        tags = [line.strip() for line in tags if not line.startswith("#")]
        tags = dict([line.split(",") for line in tags if "," in line])
    return tags


@db.atomic("EXCLUSIVE")
def import_tags(files):
    """
    import tags into the database from the files compiled by PlasTeX
    """
    tagFiles = [filename for filename in files if filename.endswith(".tag")]
    for filename in tagFiles:
        with open(
            os.path.join(flaskr.configuration.PATH, filename), encoding="utf-8"
        ) as f:
            value = f.read()

        filename = filename[:-4]
        pieces = filename.split("-")

        # store or create tag, e.g. 0001, 0GQW
        tag, created = Tag.get_or_create(tag=pieces[2].upper())

        if created:
            log.info("  Created tag %s", pieces[2])
        else:
            if tag.label != "-".join(pieces[3:]):
                log.info("  Tag %s: label has changed", tag.tag)
            if tag.html != value:
                log.info("  Tag %s: content has changed", tag.tag)
            if tag.type != pieces[0]:
                log.info("  Tag %s: type has changed", tag.tag)

        tag.label = "-".join(pieces[3:])  # original LaTeX label text
        tag.ref = pieces[1]  # e.g. 1.1, 2.3 without tailed dot
        tag.type = pieces[0]  # e.g. section, theorem
        tag.html = value
        tag.save()


@db.atomic("EXCLUSIVE")
def nameTags(tags):
    # Import and assign names to tags
    names = list()
    context = pickle.load(open(os.path.join(flaskr.configuration.PAUX), "rb"))

    labels = {item: key for key, item in tags.items()}
    for key, item in context["Gerby"].items():
        if "title" in item and key in labels:
            names.append({"tag": labels[key], "name": item["title"]})

    for entry in names:
        Tag.update(name=entry["name"]).where(Tag.tag == entry["tag"]).execute()


@db.atomic("EXCLUSIVE")
def import_proofs(files):
    proofFiles = [filename for filename in files if filename.endswith(".proof")]
    for filename in proofFiles:
        with open(
            os.path.join(flaskr.configuration.PATH, filename), encoding="utf-8"
        ) as f:
            value = f.read()

        filename = filename[:-6]
        pieces = filename.split("-")

        proof, created = Proof.get_or_create(tag=pieces[0], number=int(pieces[1]))

        if created:
            log.info("  Tag %s: created proof #%s", proof.tag.tag, proof.number)
        else:
            if proof.html != value:
                log.info("  Tag %s: proof #%s has changed", proof.tag.tag, pieces[1])

        proof.html = value

        proof.save()


if __name__ == "__main__":
    db.init(flaskr.configuration.DATABASE)

    if not os.path.isfile(flaskr.configuration.DATABASE):
        for model in [Tag, Proof]:
            model.create_table()
        log.info("Created database")

    tags = get_tags()

    files = [
        f
        for f in os.listdir(flaskr.configuration.PATH)
        if os.path.isfile(os.path.join(flaskr.configuration.PATH, f)) and f != "index"
    ]  # index is always created

    import_tags(files)

    import_proofs(files)

    nameTags(tags)
