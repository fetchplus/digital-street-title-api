from title_api.extensions import db
from sqlalchemy.sql import func
from datetime import datetime
import json

class Segment(db.Model):
    __tablename__ = 'segment'
    
    # Fields
    segment_id = db.Column(db.Integer, primary_key = True)
    created_at = db.Column(db.DateTime, nullable = False, server_default = func.now())
    coordinate_origin = db.Column(db.Float)
    coordinate_end = db.Column(db.Float)
    
    # Methods
    def __init__(self, segment_id, coordinate_origin, coordinate_end):
        self.segment_id = segment_id
        self.coordinate_origin = coordinate_origin
        self.coordinate_end = coordinate_end
      
    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys = True, separators = (',', ':'))
      
    def as_dict(self):
        return {
            "segment_id": self.segment_id,
            "coordinate_origin": self.coordinate_origin,
            "coordinate_end": self.coordinate_end,
            "created_at": self.created_at.isoformat()
        }

class Title(db.Model):
    __tablename__ = 'title'

    # Fields
    title_number = db.Column(db.String, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=True)
    lock = db.Column(db.DateTime, nullable=True)
    owner_identity = db.Column(db.Integer, db.ForeignKey('owner.identity'), nullable=False)
    address_id = db.Column(db.Integer,
                           db.ForeignKey('address.address_id', ondelete="CASCADE", onupdate="CASCADE"),
                           nullable=False)

    # Relationships
    owner = db.relationship("Owner", backref=db.backref('title', lazy='dynamic'),
                            foreign_keys='Title.owner_identity', uselist=False)
    address = db.relationship("Address", backref=db.backref('title', lazy='dynamic'),
                              foreign_keys='Title.address_id', uselist=False, cascade="all")

    # Methods
    def __init__(self, title_number, owner, address):
        self.title_number = title_number.upper()
        self.created_at = datetime.utcnow()
        self.owner = owner
        self.address = address

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "title_number": self.title_number,
            "owner": self.owner.as_dict(),
            "address": self.address.as_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else self.updated_at,
            "locked_at": self.lock.isoformat() if self.lock else self.lock
        }


class Owner(db.Model):
    __tablename__ = 'owner'

    # Fields
    identity = db.Column(db.Integer, primary_key=True, autoincrement=False)
    forename = db.Column(db.String, nullable=False)
    surname = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True, index=True)
    phone = db.Column(db.String, nullable=False)
    owner_type = db.Column(db.String, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)

    # Relationships
    address = db.relationship("Address", backref=db.backref('owner', lazy='dynamic'),
                              foreign_keys='Owner.address_id', uselist=False)

    # Methods
    def __init__(self, identity, forename, surname, email, phone, owner_type, address):
        self.identity = identity
        self.forename = forename
        self.surname = surname
        self.email = email.lower()
        self.phone = phone
        self.owner_type = owner_type
        self.address = address

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "identity": self.identity,
            "first_name": self.forename,
            "last_name": self.surname,
            "email_address": self.email,
            "phone_number": self.phone,
            "type": self.owner_type,
            "address": self.address.as_dict()
        }


class Address(db.Model):
    __tablename__ = 'address'

    # Fields
    address_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    house_name_or_number = db.Column(db.String, nullable=False)
    street_name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    county = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    postcode = db.Column(db.String, nullable=False)
    segment_id = db.Column(db.Integer, db.ForeignKey('segment.segment_id'), nullable=False)

    # Relationships
    segment = db.relationship("Segment", backref=db.backref("address", lazy='dynamic'),
                              foreign_keys='Address.segment_id', uselist=False)

    # Methods
    def __init__(self, house_name_number, street_name, city, county, country, postcode, segment):
        self.house_name_or_number = house_name_number
        self.street_name = street_name
        self.city = city
        self.county = county
        self.country = country
        self.postcode = postcode
        self.segment = segment

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "house_name_number": self.house_name_or_number,
            "street": self.street_name,
            "town_city": self.city,
            "county": self.county,
            "country": self.country,
            "postcode": self.postcode,
            "segment": self.segment.as_dict()
        }


class Conveyancer(db.Model):
    __tablename__ = 'conveyancer'

    # Fields
    conveyancer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    x500_name = db.Column(db.String, unique=True, nullable=False)
    company_name = db.Column(db.String, nullable=False)

    # Methods
    def __init__(self, x500_name, company_name):
        self.x500_name = str(x500_name)
        self.company_name = company_name

    def __repr__(self):
        return json.dumps(self.as_dict(), sort_keys=True, separators=(',', ':'))

    def as_dict(self):
        return {
            "conveyancer_id": self.conveyancer_id,
            "x500": X500Name.from_string(self.x500_name).as_dict(),
            "x500_string": str(X500Name.from_string(self.x500_name)),
            "company_name": self.company_name
        }


class X500Name(object):
    """Class representation of an X500Name."""

    # Fields
    organisation = None
    locality = None
    country = None
    state = None
    organisational_unit = None
    common_name = None

    # Methods
    def __init__(self, organisation, locality, country):
        self.organisation = organisation
        self.locality = locality
        self.country = country

    @staticmethod
    def from_string(str_obj):
        items = {}
        for item in str_obj.split(','):
            k, v = item.split('=')
            items[k.replace(' ', '')] = v

        organisation = items.get('O')
        locality = items.get('L')
        country = items.get('C')
        state = items.get('ST')
        organisational_unit = items.get('OU')
        common_name = items.get('CN')

        x500name = X500Name(organisation, locality, country)
        x500name.state = state
        x500name.organisational_unit = organisational_unit
        x500name.common_name = common_name

        x500name.validate()
        return x500name

    @staticmethod
    def from_dict(dict_obj):
        organisation = dict_obj['organisation']
        locality = dict_obj['locality']
        country = dict_obj['country']
        state = dict_obj.get('state')
        organisational_unit = dict_obj.get('organisational_unit')
        common_name = dict_obj.get('common_name')

        x500name = X500Name(organisation, locality, country)
        x500name.state = state
        x500name.organisational_unit = organisational_unit
        x500name.common_name = common_name

        x500name.validate()
        return x500name

    # Based on: https://docs.corda.net/releases/release-V3.3/generating-a-node.html#node-naming
    def validate(self):
        # Check 3 required values exist
        if not self.organisation:
            raise TypeError("Missing: organisation")
        if not self.locality:
            raise TypeError("Missing: locality")
        if not self.country:
            raise TypeError("Missing: country")

        # Check value length
        if len(self.organisation) < 2 or len(self.organisation) > 128:
            raise ValueError("Wrong length: organisation (min: 2, max: 128)")
        if len(self.locality) < 2 or len(self.locality) > 64:
            raise ValueError("Wrong length: locality (min: 2, max: 64)")
        if len(self.country) != 2:
            raise ValueError("Wrong length: country (min: 2, max: 2)")
        if self.state and (len(self.state) < 2 or len(self.state) > 64):
            raise ValueError("Wrong length: state (min: 2, max: 64)")
        if self.organisational_unit and (len(self.organisational_unit) < 2 or len(self.organisational_unit) > 64):
            raise ValueError("Wrong length: organisational_unit (min: 2, max: 64)")
        if self.common_name and (len(self.common_name) < 2 or len(self.common_name) > 64):
            raise ValueError("Wrong length: common_name (min: 2, max: 64)")

        for name, item in self.as_dict(False).items():
            if not item:
                continue

            # Check value's first letter is upper case
            if not item[0].isupper():
                raise ValueError("First character is not uppercase: " + name)

            # Check value has no leading or trailing whitespace
            if item.strip() != item:
                raise ValueError("Has leading or trailing whitespace: " + name)

            # Check value has invalid characters
            invalid_chars = [',', '=', '$', '"', '\'', '\\']
            if any(char in item for char in invalid_chars):
                raise ValueError("Contains invalid characters: " + name)

            # Check value has invalid characters
            if '\00' in item:
                raise ValueError("Contains null character: " + name)
        return True

    def __str__(self, should_validate=True):
        if should_validate:
            self.validate()

        items = []
        items.append("O=" + self.organisation)
        items.append("L=" + self.locality)
        items.append("C=" + self.country)
        if self.state:
            items.append("ST=" + self.state)
        if self.organisational_unit:
            items.append("OU=" + self.organisational_unit)
        if self.common_name:
            items.append("CN=" + self.common_name)

        return ','.join(items)

    def __repr__(self):
        return str(self)

    def as_dict(self, should_validate=True):
        if should_validate:
            self.validate()

        return {
            "organisation": self.organisation,
            "locality": self.locality,
            "country": self.country,
            "state": self.state,
            "organisational_unit": self.organisational_unit,
            "common_name": self.common_name,
        }
