
class Result():

    def __init__(self, **kwargs):
        self.kwargs = kwargs

        self.message = self.kwargs.get('message', None)
        self.level = self.kwargs.get('level', None)
        self.rule = self.kwargs.get('rule', None)
        self.filename = self.kwargs.get('filename', None)
        self.match = self.kwargs.get('match', None)
        self.match_start = self.kwargs.get('match_start', None)
        self.match_end = self.kwargs.get('match_end', None)
        self.snippet = self.kwargs.get('snippet', None)
        self.snippet_start = self.kwargs.get('snippet_start', None)
        self.snippet_end = self.kwargs.get('snippet_end', None)

    def get_location(self):
        location = {}
        if self.filename:
            location['artifactLocation'] = {"uri": self.filename}

        if self.match:
            region = {"snippet": {"text": self.match}}
            if self.match_start:
                region['startLine'] = self.match_start
            if self.match_end:
                region['endLine'] = self.match_end
            location['region'] = region

        if self.snippet:
            contextRegion = {"snippet": {"text": self.snippet}}
            if self.snippet_start:
                contextRegion['startLine'] = self.snippet_start
            if self.snippet_end:
                contextRegion['endLine'] = self.snippet_end
            location['contextRegion'] = contextRegion

        return {"physicalLocation": location}

    def to_json(self):
        final_json = {
            "message": {
                "text": self.message
            },
            "locations": [self.get_location()],
            "level": self.level,
            "ruleId": self.rule,
        }
        return final_json
