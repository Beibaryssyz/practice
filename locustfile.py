from locust import HttpUser, task, between

class ShopUser(HttpUser):
    wait_time = between(1, 3)
    host = 'https://www.demoblaze.com'

    @task(3)
    def view_homepage(self):
        with self.client.get('/', catch_response=True) as r:
            if r.status_code != 200:
                r.failure(f'Главная: ожидался 200, получен {r.status_code}')

    @task(2)
    def view_category(self):
        self.client.post('/bycat', json={'cat': 'phone'})

    @task(1)
    def view_product(self):
        self.client.post('/view', json={'id': '1'})

    @task(1)
    def check_cart(self):
        self.client.post('/viewcart', json={'cookie': 'guest', 'flag': True})
