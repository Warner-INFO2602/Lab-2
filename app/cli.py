import typer
from app.database import create_db_and_tables, get_session, drop_all
from app.models import User
from fastapi import Depends
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from typing import Annotated

cli = typer.Typer(help="CLI tool for managing User Databases.")

@cli.command()
def initialize():
    """Wipe and recreate the database with a seed user."""
    with get_session() as db:
        drop_all()
        create_db_and_tables()
        bob = User('bob', 'bob@mail.com', 'bobpass')
        db.add(bob)
        db.commit()
        db.refresh(bob)
        print("Database Initialized")

@cli.command()
def get_user(
    username: Annotated[str, typer.Argument(help="The unique username to search for")]
):
    """Retrieve a specific user by their username."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found!')
            return
        print(user)

@cli.command()
def get_all_users():
    """List all users currently in the database."""
    with get_session() as db:
        all_users = db.exec(select(User)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)

@cli.command()
def change_email(
    username: Annotated[str, typer.Argument(help="The username of the account to update")],
    new_email: Annotated[str, typer.Argument(help="The new email address to assign")]
):
    """Update the email address for an existing user."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to update email.')
            return
        user.email = new_email
        db.add(user)
        db.commit()
        print(f"Updated {user.username}'s email to {user.email}")

@cli.command()
def create_user(
    username: Annotated[str, typer.Argument(help="Desired unique username")],
    email: Annotated[str, typer.Argument(help="User's email address")],
    password: Annotated[str, typer.Argument(help="User's account password")]
):
    """Register a new user in the system."""
    with get_session() as db:
        newuser = User(username, email, password)
        try:
            db.add(newuser)
            db.commit()
        except IntegrityError:
            db.rollback()
            print("Username or email already taken!")
        else:
            print(newuser)

@cli.command()
def delete_user(
    username: Annotated[str, typer.Argument(help="The username to permanently delete")]
):
    """Remove a user from the database."""
    with get_session() as db:
        user = db.exec(select(User).where(User.username == username)).first()
        if not user:
            print(f'{username} not found! Unable to delete user.')
            return
        db.delete(user)
        db.commit()
        print(f'{username} deleted')

@cli.command()
def search_user(
    string: Annotated[str, typer.Argument(help="The partial string to match against usernames or emails")]
):
    """Search for users where the username or email contains a specific string."""
    with get_session() as db:
        users = db.exec(select(User).where(User.username.contains(string) | User.email.contains(string))).all()
        if not users:
            print(f'{string} not found!')
            return
        else:
            for user in users:
                print(user)

@cli.command()
def page_users(
    limit: Annotated[int, typer.Argument(help="Number of records to return")] = 10,
    offset: Annotated[int, typer.Argument(help="Number of records to skip")] = 0
):
    """Paginate through users using SQL OFFSET and LIMIT."""
    with get_session() as db:
        all_users = db.exec(select(User).offset(offset).limit(limit)).all()
        if not all_users:
            print("No users found")
        else:
            for user in all_users:
                print(user)

if __name__ == "__main__":
    cli()