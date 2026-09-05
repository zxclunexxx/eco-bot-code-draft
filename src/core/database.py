from contextlib import contextmanager
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from src.config import get_settings
from src.core.models import Base, EcoTip, Material, PointMaterial, RecyclingPoint


settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    seed_initial_data()


@contextmanager
def db_session():
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def seed_initial_data() -> None:
    with SessionLocal() as session:
        has_materials = session.scalar(select(Material).limit(1))
        if has_materials:
            return

        materials = [
            Material(name="Пластик"),
            Material(name="Бумага"),
            Material(name="Стекло"),
            Material(name="Металл"),
            Material(name="Батарейки"),
            Material(name="Одежда"),
            Material(name="Электроника"),
        ]
        session.add_all(materials)
        session.flush()

        points = [
            RecyclingPoint(
                name="ЭкоПункт Центральный",
                address="ул. Зелёная, 10",
                latitude=55.751244,
                longitude=37.618423,
                working_hours="Пн–Пт 09:00–18:00",
                conditions="Принимаются чистые и отсортированные отходы.",
            ),
            RecyclingPoint(
                name="Раздельный сбор Север",
                address="пр-т Экологов, 25",
                latitude=55.761244,
                longitude=37.608423,
                working_hours="Ежедневно 10:00–20:00",
                conditions="Пластик нужно промыть, батарейки сдавать отдельно.",
            ),
            RecyclingPoint(
                name="Пункт приёма Стекло+",
                address="ул. Солнечная, 3",
                latitude=55.741244,
                longitude=37.628423,
                working_hours="Сб–Вс 11:00–17:00",
                conditions="Принимается стекло без остатков жидкости.",
            ),
        ]
        session.add_all(points)
        session.flush()

        material_by_name = {m.name: m for m in materials}
        links = [
            (points[0], "Пластик"),
            (points[0], "Бумага"),
            (points[0], "Батарейки"),
            (points[1], "Пластик"),
            (points[1], "Металл"),
            (points[1], "Электроника"),
            (points[2], "Стекло"),
        ]
        session.add_all([
            PointMaterial(point_id=point.id, material_id=material_by_name[name].id)
            for point, name in links
        ])

        tips = [
            EcoTip(text="Сдавайте батарейки отдельно: они содержат вещества, опасные для почвы."),
            EcoTip(text="Перед сдачей пластика промойте упаковку и сожмите её, чтобы она занимала меньше места."),
            EcoTip(text="Используйте многоразовую бутылку вместо одноразовой пластиковой тары."),
            EcoTip(text="Сортируйте бумагу отдельно от влажных отходов, иначе её сложнее переработать."),
        ]
        session.add_all(tips)
        session.commit()
