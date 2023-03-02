import json


class Sarif():

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        if self.kwargs.get('name', None):
            self.tool_name = self.kwargs.get('name')
        self.results = []
        self.rules = []

    def add_rule(self, ruleID, name, helpUri=""):
        r = {
            "id": ruleID,
            "name": name,
            "helpUri": helpUri
        }
        if r not in self.rules:
            self.rules.append(r)

    def to_json(self):
        final_json = {}
        if self.tool_name:
            final_json['tool'] = {'driver': {'name': self.tool_name, "rules": self.rules}}
        results = []
        for r in self.results:
            results.append(r.to_json())
        final_json['results'] = results
        return {
            "version": "2.1.0",
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json",
            "runs": [final_json]
        }

    def add_result(self, r):
        self.results.append(r)

    def __repr__(self):
        return json.dumps(self.to_json())
