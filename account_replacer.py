import ast

__plugins__ = ["account_replacer"]

import re

from beancount.core import data


class AccountReplacer:

    def replace(self, entries, options_map, config_str=""):
        config = {}
        expr = ast.literal_eval(config_str)
        config.update(expr)

        replace_rules = config.get("replace-rules")
        if replace_rules is None or len(replace_rules) == 0:
            return entries, []

        new_entries = []
        for entry in entries:
            new_entry = entry

            for replace_rule in replace_rules:
                new_entry = self.__replace_entry(new_entry, replace_rule)

            new_entries.append(new_entry)

        return new_entries, []

    def __replace_entry(self, entry, replace_rule):

        if isinstance(entry, data.Transaction):
            new_postings = []
            for posting in entry.postings:
                account = posting.account
                new_account = re.sub(replace_rule["replace-from"], replace_rule["replace-to"], account)
                new_postings.append(posting._replace(account=new_account))

            return entry._replace(postings=new_postings)
        elif isinstance(entry, data.Open) or isinstance(entry, data.Close) or isinstance(entry, data.Balance):
            new_account = re.sub(replace_rule["replace-from"], replace_rule["replace-to"], entry.account)
            return entry._replace(account=new_account)
        elif isinstance(entry, data.Pad):
            new_account = re.sub(replace_rule["replace-from"], replace_rule["replace-to"], entry.account)
            new_source_account = re.sub(replace_rule["replace-from"], replace_rule["replace-to"], entry.source_account)
            return entry._replace(account=new_account, source_account=new_source_account)

        return entry


account_replacer_obj = AccountReplacer()


def account_replacer(entries, options_map, config_str=""):
    return account_replacer_obj.replace(entries, options_map, config_str)
