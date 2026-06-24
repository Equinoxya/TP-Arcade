import inquirer
from database import engine, Borne, Games_types, Game, Status
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

Session = sessionmaker(bind=engine)
session = Session()


class ArcadeManager:
    def __init__(self, session):
        self.session = session

    def add_borne(self):
        games_types_list = self.session.scalars(select(Games_types)).all()
        availability = self.session.scalars(select(Status)).all()
        games_list = self.session.scalars(select(Game)).all()

        choices_types = [gt.name for gt in games_types_list]
        choices_available = [a.name for a in availability]
        choices_games = [g.name for g in games_list]

        questions = [
            inquirer.Text('nom', message="Quel est le nom de la borne ?"),
            inquirer.List('type', message='Quel type de jeu ?', choices=choices_types),
            inquirer.Text('prix', message="Quel est le prix d'une partie ?"),
            inquirer.List('status', message='Quel est son statut ?', choices=choices_available),
            inquirer.List('game', message='Quel jeu est installé ?', choices=choices_games),
        ]
        answers = inquirer.prompt(questions)

        # On récupère les objets pour avoir leurs id (FK)
        status_obj = self.session.scalars(select(Status).where(Status.name == answers['status'])).first()
        type_obj = self.session.scalars(select(Games_types).where(Games_types.name == answers['type'])).first()
        game_obj = self.session.scalars(select(Game).where(Game.name == answers['game'])).first()

        borne = Borne(
            name=answers['nom'],
            borne_type=type_obj.id,
            price=float(answers['prix']),
            status_id=status_obj.id,
            game_id=game_obj.id,
            nb_games=0
        )
        self.session.add(borne)
        self.session.commit()
        print("Borne ajoutée ✓")

    def display_all(self):
        bornes = self.session.execute(
            select(Borne, Games_types.name, Status.name)
            .join(Games_types, Borne.borne_type == Games_types.id)
            .join(Status, Borne.status_id == Status.id)
        ).all()

        print('======== Toutes les bornes ========')
        for borne, type_name, status_name in bornes:
            print(
                f"Nom : {borne.name} || {type_name} || "
                f"{borne.price}€ par partie || Statut : {status_name} || "
                f"Parties jouées : {borne.nb_games}\n"
            )

    def display_dispo(self):
        result = self.session.execute(
            select(Borne.name, Borne.price, Status.name)
            .join(Status)
            .where(Status.name == "Disponible")
        ).all()

        print('======== Bornes disponibles ========')
        for name, price, statut in result:
            print(f"Nom : {name} || {price}€ par partie || {statut}\n")

    def start_game(self):
        borne_dispo = self.session.scalars(
            select(Borne).join(Status).where(Status.name == "Disponible")
        ).all()

        if not borne_dispo:
            print("Aucune borne disponible")
            return

        choices = [borne.name for borne in borne_dispo]
        answer = inquirer.prompt([
            inquirer.List("borne", message="Sur quelle borne lancer la partie ?", choices=choices)
        ])

        borne = self.session.scalars(select(Borne).where(Borne.name == answer["borne"])).first()
        status = self.session.scalars(select(Status).where(Status.name == "Occupée")).first()
        borne.status_id = status.id
        borne.nb_games += 1
        self.session.commit()
        print(f"Partie lancée sur {borne.name} ✓")

    def end_game(self):
        borne_occupee = self.session.scalars(
            select(Borne).join(Status).where(Status.name == "Occupée")
        ).all()

        if not borne_occupee:
            print("Aucune borne n'est occupée")
            return

        choices = [borne.name for borne in borne_occupee]
        answer = inquirer.prompt([
            inquirer.List("borne", message="Sur quelle borne terminer la partie ?", choices=choices)
        ])

        borne = self.session.scalars(select(Borne).where(Borne.name == answer["borne"])).first()
        status = self.session.scalars(select(Status).where(Status.name == "Disponible")).first()
        borne.status_id = status.id
        self.session.commit()
        print(f"Partie terminée sur {borne.name} ✓")

    def maintenance(self):
        bornes = self.session.scalars(select(Borne)).all()
        choices = [borne.name for borne in bornes]
        answer = inquirer.prompt([
            inquirer.List("borne", message="Quelle borne mettre en maintenance ?", choices=choices)
        ])

        borne = self.session.scalars(select(Borne).where(Borne.name == answer["borne"])).first()
        status = self.session.scalars(select(Status).where(Status.name == "Maintenance")).first()
        borne.status_id = status.id
        self.session.commit()
        print(f"{borne.name} mise en maintenance ✓")

    def statistics(self):
        total_bornes = self.session.scalar(select(func.count()).select_from(Borne))
        dispo = self.session.scalar(
            select(func.count()).select_from(Borne).join(Status).where(Status.name == "Disponible")
        )
        occupees = self.session.scalar(
            select(func.count()).select_from(Borne).join(Status).where(Status.name == "Occupée")
        )
        maintenance = self.session.scalar(
            select(func.count()).select_from(Borne).join(Status).where(Status.name == "Maintenance")
        )
        total_games = sum(borne.nb_games for borne in self.session.scalars(select(Borne)).all())
        borne_populaire = self.session.scalars(
            select(Borne).order_by(Borne.nb_games.desc())
        ).first()

        print("\n===== STATISTIQUES =====")
        print(f"Nombre total de bornes    : {total_bornes}")
        print(f"Bornes disponibles        : {dispo}")
        print(f"Bornes occupées           : {occupees}")
        print(f"Bornes en maintenance     : {maintenance}")
        print(f"Parties jouées au total   : {total_games}")
        if borne_populaire:
            print(f"Borne la plus utilisée    : {borne_populaire.name} ({borne_populaire.nb_games} parties)")


def menu():
    manager = ArcadeManager(session)

    actions = {
        "Ajouter une borne": manager.add_borne,
        "Afficher toutes les bornes": manager.display_all,
        "Afficher toutes les bornes disponibles": manager.display_dispo,
        "Lancer une partie": manager.start_game,
        "Terminer une partie": manager.end_game,
        "Mettre une borne en maintenance": manager.maintenance,
        "Afficher les statistiques": manager.statistics,
        "Quitter": exit,
    }

    while True:
        result = inquirer.prompt([
            inquirer.List('Menu', message='Que voulez-vous faire ?', choices=list(actions.keys()))
        ])
        actions[result['Menu']]()


if __name__ == "__main__":
    menu()