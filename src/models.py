from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

#tabla de asociacion para relacion m2m
class Favorites(db.Model):
    __tablename__="favorites"
    id: Mapped[int] = mapped_column(primary_key=True)

    #claves foraneas 
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    planet_id: Mapped[int] = mapped_column(ForeignKey("planets.id"), nullable=True) #puede estar varcio
    people_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=True) #puede estar varcio

    #relacion --> tipo de relacion que tenemos
    user: Mapped["User"] = relationship(back_populates="favorites")
    planet: Mapped["Planets"] = relationship(back_populates="favorites")
    people: Mapped["People"] = relationship(back_populates="favorites")

    def serialize(self):
        return{
            "id": self.id,
            "user": {
                "id": self.user.id
            },
            "planet":{
                "id": self.planet.id,
                "name": self.planet.name
            },
            "people": {
                "id": self.people.id,
                "name": self.people.name,
                "hair_color": self.people.hair_color
            }
        }



class User(db.Model):
    __tablename__="user"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    #relacion
    #m2m
    favorites: Mapped[List["Favorites"]] = relationship(back_populates="user")
    #1-1
    profile: Mapped['Profile'] = relationship(back_populates="user")
    #M-1
    posts: Mapped[List["Posts"]] = relationship(back_populates='author')

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
            # relacion 1-1, se serializa directamente
            "profile": self.profile.serialize() if self.profile else None,
            #es un lista, se serializa utilizando un loop, ya sea map, lista comprensiva y se tiene que verificar que exista informacion
            "posts": [post.serialize() for post in self.posts] if self.posts else None,
            "favorites": [fav.serialize() for fav in self.favorites] if self.favorites else None
        }



class People(db.Model):
    __tablename__="people"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(10), nullable=False)
    
    #relacion
    favorites: Mapped[List["Favorites"]] = relationship(back_populates="people")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "favorites": [fav.serialize() for fav in self.favorites] if self.favorites else None

        }


class Planets(db.Model):
    __tablename__="planets"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(40), nullable=False)
    weather: Mapped[str] = mapped_column(String(10), nullable=False)

    #relacion
    favorites: Mapped[List["Favorites"]] = relationship(back_populates="planet")
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "weather": self.weather,
            "favorites": [fav.serialize() for fav in self.favorites] if self.favorites else None

        }


class Profile(db.Model):
    __tablename__="profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    bio: Mapped[str] = mapped_column(Text)
    #clave foranea
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    #relacion 1-1. No hay lista
    user: Mapped['User'] = relationship(back_populates="profile") #almacena objeto que viene de tabla user

    def serialize(self):
        return {
            "id": self.id,
            "bio": self.bio,
            #pasar a diccionario el objeto cuando devolvemos la informacion al endpoint
            "user": self.user.serialize() if self.user else None
        }

class Posts(db.Model):
    __tablename__="posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    #clave foranea
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    #relacion M-1
    author: Mapped["User"] = relationship(back_populates='posts')
    
    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "body": self.body,
            #es un author por post, no es una lista, podemos serializar directamente
            "author": self.author.serialize() if self.author else None
        }