import os
from dataclasses import dataclass

from requests import Session


class FlowerURL:
    BASE_URL = os.environ.get("FLOWER_URL", "http://localhost:5555/api")
    TASKS = {'url': f'{BASE_URL}/tasks', 'method': 'GET'}
    TASK_TYPES = {'url': f'{BASE_URL}/task/types', 'method': 'GET'}
    TASK_INFO = {'url': f'{BASE_URL}/task/info/%s', 'method': 'GET'}


@dataclass
class FlowerClient:
    session: Session = Session()
    urls: FlowerURL = FlowerURL()

    def fetch(self, http_request: dict, **kwargs):
        try:
            result = self.session.request(**http_request, **kwargs)
            return result.json()
        except Exception as err:
            print(err)
            return {}

    def get_tasks(
        self,
        page_size: int = 10,
        page: int = 1,
        state: str = "",
        taskname: str = "",
        sort_field: str = "",
        order_type: bool = True,
        **kwargs
    ):
        params = kwargs.pop('params', {})
        params['limit'] = page_size
        params['offset'] = (page - 1) * page_size
        params['state'] = state
        params['taskname'] = taskname
        if sort_field:
            params['sort_by'] = sort_field if order_type else f"-{sort_field}"

        resp = self.fetch(self.urls.TASKS, params=params, **kwargs)
        return [v for _, v in resp.items()]

    def get_task_type(self):
        return self.fetch(self.urls.TASK_TYPES)['task-types']

    def get_task(self, uuid: str):
        url_method = self.urls.TASK_INFO.copy()
        url_method['url'] = url_method['url'] % uuid
        return self.fetch(url_method)


# if __name__ == '__main__':
#     f = FlowerClient()
#     pprint(f.get_task('d0a49e1b-6e78-49b2-873e-2f425a822d10'))
#     pprint(f.get_task('d0a49e1b-6e78-49b2-873e-2f425a822d10'))
