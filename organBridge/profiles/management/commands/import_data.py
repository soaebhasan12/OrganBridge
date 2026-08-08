import json
from codecs import BOM_UTF16_LE, BOM_UTF16_BE, BOM_UTF8
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from matches.models import MatchMessage, MatchPreference, OrganMatch
from profiles.models import DonorProfile, RecipientProfile


CustomUser = get_user_model()


class Command(BaseCommand):
    help = "Import local fixture data into the current database without overwriting existing accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fixture",
            default="data.json",
            help="Path to the fixture file exported with dumpdata.",
        )

    def handle(self, *args, **options):
        fixture_path = Path(options["fixture"])
        if not fixture_path.is_absolute():
            fixture_path = settings.BASE_DIR / fixture_path

        if not fixture_path.exists():
            raise CommandError(f"Fixture file not found: {fixture_path}")

        objects = load_fixture_json(fixture_path)

        created_users = 0
        created_donor_profiles = 0
        created_recipient_profiles = 0
        created_matches = 0
        created_messages = 0
        created_preferences = 0

        user_by_pk = {}
        match_by_pk = {}

        for obj in objects:
            model = obj.get("model")
            fields = obj.get("fields", {})

            if model == "accounts.customuser":
                username = fields.get("username")
                if not username:
                    continue

                user, created = CustomUser.objects.get_or_create(
                    username=username,
                    defaults=fields,
                )
                if created:
                    created_users += 1
                user_by_pk[obj["pk"]] = user

        for obj in objects:
            model = obj.get("model")
            fields = obj.get("fields", {})

            if model == "profiles.donorprofile":
                user = user_by_pk.get(fields.get("user"))
                if not user or hasattr(user, "donor_profile"):
                    continue

                DonorProfile.objects.create(user=user, **fields_remap(fields, {"user"}))
                created_donor_profiles += 1

            elif model == "profiles.recipientprofile":
                user = user_by_pk.get(fields.get("user"))
                if not user or hasattr(user, "recipient_profile"):
                    continue

                RecipientProfile.objects.create(user=user, **fields_remap(fields, {"user"}))
                created_recipient_profiles += 1

            elif model == "matches.organmatch":
                donor = user_by_pk.get(fields.get("donor"))
                recipient = user_by_pk.get(fields.get("recipient"))
                if not donor or not recipient:
                    continue

                match, created = OrganMatch.objects.get_or_create(
                    donor=donor,
                    recipient=recipient,
                    defaults=fields_remap(fields, {"donor", "recipient"}),
                )
                if created:
                    created_matches += 1
                match_by_pk[obj["pk"]] = match

            elif model == "matches.matchmessage":
                match_pk = fields.get("match")
                match = match_by_pk.get(match_pk)
                sender = user_by_pk.get(fields.get("sender"))
                if not match or not sender:
                    continue

                message, created = MatchMessage.objects.get_or_create(
                    match=match,
                    sender=sender,
                    message=fields.get("message", ""),
                    defaults=fields_remap(fields, {"match", "sender"}),
                )
                if created:
                    created_messages += 1

            elif model == "matches.matchpreference":
                user = user_by_pk.get(fields.get("user"))
                if not user or hasattr(user, "matchpreference"):
                    continue

                MatchPreference.objects.create(
                    user=user,
                    **fields_remap(fields, {"user"}),
                )
                created_preferences += 1

        self.stdout.write(self.style.SUCCESS(
            "Imported fixture data. "
            f"Users: {created_users}, Donors: {created_donor_profiles}, "
            f"Recipients: {created_recipient_profiles}, Matches: {created_matches}, "
            f"Messages: {created_messages}, Preferences: {created_preferences}"
        ))


def fields_remap(fields, excluded_keys):
    remapped = {}
    for key, value in fields.items():
        if key not in excluded_keys:
            remapped[key] = value
    return remapped


def load_fixture_json(fixture_path):
    raw = fixture_path.read_bytes()

    if raw.startswith(BOM_UTF16_LE) or raw.startswith(BOM_UTF16_BE):
        text = raw.decode("utf-16")
    elif raw.startswith(BOM_UTF8):
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8")

    return json.loads(text)
