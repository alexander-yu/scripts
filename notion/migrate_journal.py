import datetime
import re
import typing

import click

from boltons import iterutils
from notion import block, collection

import client


WEEKDAYS = '|'.join(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
ENTRY_TITLE_REGEX = fr'(?:{WEEKDAYS}), (?P<month>\d+)/(?P<day>\d+)'


def get_entries(backstop: datetime.date = None) -> typing.Tuple[datetime.date, block.BulletedListBlock]:
    journal = iterutils.first(
        client.notion_client().get_top_level_pages(),
        key=lambda page: page.title == 'Journal',
    )

    if not journal:
        raise ValueError('No journal found with name \'Journal\'')

    for year in journal.children:
        for month in year.children:
            for week in month.children:
                for entry in week.children:
                    match = re.fullmatch(ENTRY_TITLE_REGEX, entry.title)
                    assert match is not None, (year, month, week, entry)

                    date = datetime.date(
                        int(year.title),
                        int(match.group('month')),
                        int(match.group('day')),
                    )
                    if backstop and date < backstop:
                        continue

                    yield date, entry


def migrate_entry(
    journal: collection.Collection,
    date: datetime.date,
    entry: block.BulletedListBlock,
):
    new_row = journal.add_row(date=date, title=str(date))
    copy_children(entry, new_row)


def copy_children(old: block.Block, new: block.Block):
    for old_child in old.children:
        new_child = new.children.add_new(old_child.__class__, title=old_child.title)
        copy_children(old_child, new_child)


@click.command()
@click.option('--backstop', type=click.DateTime())
def cli(backstop: datetime.datetime):
    journal = iterutils.first(
        client.notion_client().get_top_level_pages(),
        key=lambda page: page.title == 'Journal (New)',
    )

    if not journal:
        raise ValueError('No journal found with name \'Journal (New)\'')

    for date, entry in get_entries(backstop=backstop.date()):
        migrate_entry(journal.collection, date, entry)
        click.echo(f'Migrated {date}')


if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    cli()
