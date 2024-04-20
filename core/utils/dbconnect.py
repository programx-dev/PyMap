import asyncpg


class Request:
    def __init__(self, connector: asyncpg.pool.Pool):
        self.connector = connector

    def list_to_array(self, lst: list):
        lst = str(list(map(str, lst)))
        lst = lst.replace("[", "{").replace("]", "}").replace("\'", "\"")
        return lst

    async def add_data_user(self, user_id, user_name):
        query = f"INSERT INTO users (user_id, user_name, correct_quizzes, wrong_quizzes, newsletter)"\
                f"VALUES ({user_id}, '{user_name}', $1, $2, true)"\
                f"ON CONFLICT (user_id) DO UPDATE SET user_name='{user_name}'"
        await self.connector.execute(query, list(), list())

    async def set_user_settings(self, user_id, user_name, newsletter):
        query = f"INSERT INTO users (user_id, user_name, newsletter)"\
                f"VALUES ({user_id}, '{user_name}', $1)"\
                f"ON CONFLICT (user_id) DO UPDATE SET user_name='{user_name}', newsletter=$1"
        await self.connector.execute(query, newsletter)

    async def get_data_users(self, user_id: int) -> list:
        query = f"SELECT * FROM users WHERE user_id={user_id}"
        return await self.connector.fetchrow(query)

    async def get_data_roadmap(self, id: int) -> list:
        query = f"SELECT * FROM roadmap WHERE id={id}"
        return await self.connector.fetchrow(query)

    async def get_data_test(self, id: int) -> list:
        query = f"SELECT * FROM tests WHERE id={id}"
        return await self.connector.fetchrow(query)

    async def get_max_id_quizze(self) -> list:
        query = f"SELECT id FROM quizzes ORDER BY id DESC"
        return await self.connector.fetchval(query)

    async def get_data_quizze(self, id: int) -> list:
        query = f"SELECT * FROM quizzes WHERE id={id}"
        return await self.connector.fetchrow(query)

    async def add_data_correct_quizzes(self, user_id, user_name, quizze_id: int) -> list:
        query = f"SELECT correct_quizzes, wrong_quizzes FROM users WHERE user_id={user_id}"
        correct_quizzes, wrong_quizzes = (await self.connector.fetch(query))[0].values()
        
        correct_quizzes = set(correct_quizzes)
        correct_quizzes.add(quizze_id)
        correct_quizzes = list(correct_quizzes)

        wrong_quizzes = set(wrong_quizzes)
        wrong_quizzes.discard(quizze_id)
        wrong_quizzes = list(wrong_quizzes)

        await self.__update_data_users(user_id, user_name, correct_quizzes, wrong_quizzes)

    async def add_data_wrong_quizzes(self, user_id, user_name, quizze_id: int) -> list:
        query = f"SELECT correct_quizzes, wrong_quizzes FROM users WHERE user_id={user_id}"
        correct_quizzes, wrong_quizzes = (await self.connector.fetch(query))[0].values()

        correct_quizzes = set(correct_quizzes)
        correct_quizzes.discard(quizze_id)
        correct_quizzes = list(correct_quizzes)

        wrong_quizzes = set(wrong_quizzes)
        wrong_quizzes.add(quizze_id)
        wrong_quizzes = list(wrong_quizzes)

        await self.__update_data_users(user_id, user_name, correct_quizzes, wrong_quizzes)

    async def __update_data_users(self, user_id, user_name, correct_quizzes: list, wrong_quizzes: list): 
        query = f"INSERT INTO users (user_id, user_name, correct_quizzes, wrong_quizzes)"\
                f"VALUES ({user_id}, '{user_name}', $1, $2)"\
                f"ON CONFLICT (user_id) DO UPDATE SET (user_name, correct_quizzes, wrong_quizzes) = ('{user_name}', $1, $2)"
        await self.connector.execute(query, correct_quizzes, wrong_quizzes)

    async def check_table(self, name_table):
        query = f"SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = '{name_table}');"
        return await self.connector.fetchval(query)

    async def create_table(self, name_table):
        query = f"CREATE TABLE {name_table} (user_id bigint NOT NULL, statuse text, description text, PRIMARY KEY (user_id));"
        await self.connector.execute(query)

        query = f"INSERT INTO {name_table} (user_id, statuse, description) SELECT user_id, 'waiting', null FROM users"
        await self.connector.execute(query)

    async def delete_table(self, name_table):
        query = f"DROP TABLE {name_table};"
        await self.connector.execute(query)