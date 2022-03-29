from typing import List, Optional


class RequestParams:
    async def get_query(self,
                        params: dict,
                        index: str,
                        search_fields: Optional[List] = None,
                        ) -> dict:
        # Парсит параметры и формирует запрос в elastic
        _index = params.get('_index')
        query_body = params.get('query_body')
        search_text = params.get('search_text')
        filter = params.get('filter[genre]')
        page_number = int(params.get('page[number]'))
        page_size = int(params.get('page[size]'))
        sort = params.get('sort')

        if not _index:
            _index = index

        if not query_body:
            query_body: dict = {'query': {'match_all': {}}}

        if filter:
            query_body = {
                'query': {
                    'nested': {
                        'path': 'genre',
                        'query': {
                            'bool': {
                                'must': [
                                    {'term': {'genre.id': filter}},
                                ]
                            }
                        }
                    }
                }
            }

        if search_text:
            query_body: dict = {
                'query': {
                    'multi_match': {
                        'query': search_text,
                        'fuzziness': 'auto',
                        'fields': search_fields
                    }
                }
            }

        sort_field = sort[0] if not isinstance(sort, str) and sort else sort
        if sort_field:
            order = 'desc' if sort_field.startswith('-') else 'asc'
            sort_field = f"{sort_field.removeprefix('-')}:{order}"

        query = {
            'index': _index,
            'body': query_body,
            'sort': sort_field,
            'size': page_size,
            'from_': (page_number - 1) * page_size
        }

        query = {key: value for key, value in query.items()
                 if value is not None}

        return query
