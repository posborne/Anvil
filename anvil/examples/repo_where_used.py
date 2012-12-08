
from anvil import Anvil
from anvil.entities import KilnRepo

def main():
    anvil = Anvil("spectrum")
    anvil.create_session_by_prompting()
    res = anvil.get_json("/Repo/68219")
    repo = KilnRepo.from_json(anvil, res)
    subrepos = repo.where_used()

if __name__ == '__main__':
    main()
