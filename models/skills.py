# -*- coding: utf-8 -*-
from .db import db

class Skills(db.Model):
    __tablename__ = 'skills'

    id = db.Column('skill_id', db.Integer, primary_key=True)
    skill_name = db.Column(db.String(20), nullable=False, unique=True)

    @staticmethod
    def get_by_name(name):
        return Skills.query.filter(Skills.skill_name == name).scalar()

    @staticmethod
    def get_by_id(id):
        return Skills.query.filter(Skills.id == id).scalar()

    def to_json(self):
        return dict(
            id=self.id,
            skill_name=self.skill_name
        )

    def __repr__(self):
        return '<Skill %d>' % self.id