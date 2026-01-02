# from typing import Any, Dict, Optional
# import json
# from mistralai import Mistral
# # from groq import Groq
# from app.supabase_client import supabase
# from app.settings import MISTRAL_API_KEY, ENTITY_EXTRACT_SYSTEM_PROMPT


# class KyvoEngine:
#     def __init__(self):
#         self.mistral_client = Mistral(api_key=MISTRAL_API_KEY)

#     # --------------------------------------------------
#     # Utilities
#     # --------------------------------------------------
#     def safe_json_load(self, s: str) -> Dict[str, Any]:
#         s = s.strip()
#         try:
#             return json.loads(s)
#         except Exception:
#             if "{" in s and "}" in s:
#                 s = s[s.index("{"): s.rindex("}") + 1]
#                 return json.loads(s)
#             raise

#     # --------------------------------------------------
#     # Entity extraction
#     # --------------------------------------------------
#     def extract_entities(self, user_query: str) -> Dict[str, Any]:
#         resp = self.mistral_client.chat.complete(
#             model="mistral-medium-latest",
#             messages=[
#                 {"role": "system", "content": ENTITY_EXTRACT_SYSTEM_PROMPT},
#                 {"role": "user", "content": user_query},
#             ],
#             temperature=0.0,
#         )

#         content = resp.choices[0].message.content
#         data = self.safe_json_load(content)

#         template = {
#             "bore_d_mm": None,
#             "outer_D_mm": None,
#             "width_B_mm": None,
#             "life_hours": None,
#             "rpm": None,
#             "radial_load_kN": None,
#             "axial_load_kN": None,
#             "bearing_type": None,
#             "brand": None,
#             "designation": None,
#             "application_hint": None,
#         }

#         for k in template:
#             if k not in data:
#                 data[k] = None

#         return data

#     # --------------------------------------------------
#     # Intent
#     # --------------------------------------------------
#     def decide_intent(self, entities: Dict[str, Any]) -> Dict[str, Any]:
#         life = entities.get("life_hours")
#         radial = entities.get("radial_load_kN")
#         application_hint = entities.get("application_hint")

#         if life is not None or radial is not None:
#             return {
#                 "intent": "ENGINEERING_SELECTION",
#                 "missing_fields": [],
#                 "reason": "Life or load specified → engineering calculation required."
#             }

#         if application_hint is not None:
#             return {
#                 "intent": "ENGINEERING_SELECTION",
#                 "missing_fields": [],
#                 "reason": "Application-based request → derive engineering parameters."
#             }

#         return {
#             "intent": "DIRECT_SEARCH",
#             "missing_fields": [],
#             "reason": "No engineering or application requirement → direct catalogue search."
#         }

#     # --------------------------------------------------
#     # Defaults from application
#     # --------------------------------------------------
#     def derive_defaults_from_application(self, application_hint: str):
#         ah = application_hint.lower()

#         if ah in ["slewing", "slewing_ring", "turntable", "yaw_drive", "excavator", "rotary_table"]:
#             return {"life_hours": 12000, "rpm": 50, "radial_load_kN": 30.0, "axial_load_kN": 10.0}

#         if ah in ["conveyor", "conveyors", "crusher", "crushers", "cement_mill",
#                   "rolling_mill", "paper_dryer", "large_pump"]:
#             return {"life_hours": 8000, "rpm": 300, "radial_load_kN": 10.0, "axial_load_kN": 0.0}

#         if ah in ["gearbox", "gearboxes", "industrial_pump", "fan",
#                   "low_speed_motor", "compressor", "rubber_mixer"]:
#             return {"life_hours": 8000, "rpm": 1500, "radial_load_kN": 8.0, "axial_load_kN": 2.0}

#         if ah in ["automotive_wheel", "propeller_shaft", "engine",
#                   "rocker_arm", "reducer", "machinery_spindle"]:
#             return {"life_hours": 6000, "rpm": 3000, "radial_load_kN": 6.0, "axial_load_kN": 1.5}

#         if ah in ["household", "household_appliance", "small_motor",
#                   "blower", "light_rolling_mill", "automotive_transmission"]:
#             return {"life_hours": 3000, "rpm": 7000, "radial_load_kN": 2.0, "axial_load_kN": 0.5}

#         if ah in ["machine_tool_spindle", "turbocharger",
#                   "high_speed_pump", "dental_drill", "small_turbine"]:
#             return {"life_hours": 2000, "rpm": 15000, "radial_load_kN": 1.5, "axial_load_kN": 0.5}

#         if ah in ["air_compressor", "high_performance_motor",
#                   "precision_grinder", "textile_spindle"]:
#             return {"life_hours": 1500, "rpm": 25000, "radial_load_kN": 1.0, "axial_load_kN": 0.3}

#         if ah in ["gas_turbine", "aerospace", "high_speed_spindle", "gyroscope"]:
#             return {"life_hours": 1000, "rpm": 60000, "radial_load_kN": 0.5, "axial_load_kN": 0.2}

#         if ah in ["ultra_high_speed", "advanced_turbine", "laboratory_equipment"]:
#             return {"life_hours": 500, "rpm": 120000, "radial_load_kN": 0.2, "axial_load_kN": 0.1}

#         return None

#     # --------------------------------------------------
#     # Life + application inference
#     # --------------------------------------------------
#     def classify_life_hours(self, life_hours: float):
#         if life_hours < 300:
#             return {"life_class": "very_low", "life_comment": "Very short specification life"}
#         elif 300 <= life_hours <= 3000:
#             return {"life_class": "light_duty", "life_comment": "Typical for household, agricultural, or medical equipment"}
#         elif 3000 < life_hours <= 8000:
#             return {"life_class": "intermittent_industrial", "life_comment": "Typical for intermittent industrial or construction machinery"}
#         elif 8000 < life_hours <= 12000:
#             return {"life_class": "high_reliability", "life_comment": "High reliability application such as lifts or cranes"}
#         else:
#             return {"life_class": "very_high_reliability", "life_comment": "Very high life expectation; conservative bearing selection required"}

#     def infer_application_from_rpm_and_life(self, rpm: float, life_hours: float):
#         if rpm < 100:
#             return {"application_class": "slewing_positioning", "examples": ["slewing drives", "positioning systems"]}
#         elif 100 <= rpm <= 500:
#             return {"application_class": "low_speed_industrial", "examples": ["conveyors", "crushers"]}
#         elif 500 < rpm <= 2000:
#             if life_hours > 8000:
#                 return {"application_class": "high_reliability_industrial", "examples": ["gearboxes", "pumps", "continuous-duty machinery"]}
#             return {"application_class": "general_industrial", "examples": ["gearboxes", "pumps"]}
#         elif 2000 < rpm <= 5000:
#             return {"application_class": "automotive", "examples": ["automotive systems"]}
#         elif 5000 < rpm <= 10000:
#             return {"application_class": "small_motors", "examples": ["electric motors", "household machines"]}
#         else:
#             return {"application_class": "high_speed", "examples": ["spindles", "turbomachinery"]}

#     # --------------------------------------------------
#     # Engineering
#     # --------------------------------------------------
#     def compute_engineering_requirements(self, entities: Dict[str, Any], category_hint: Optional[str] = None):
#         life_hours = entities["life_hours"]
#         rpm = entities["rpm"]
#         Fr = entities["radial_load_kN"]
#         Fa = entities.get("axial_load_kN") or 0.0

#         L10 = (life_hours * 60 * rpm) / 1_000_000
#         P = Fr + Fa

#         p = 10 / 3
#         if category_hint and "ball" in category_hint.lower():
#             p = 3

#         C_required = P * (L10 ** (1 / p))

#         return {
#             "L10_million_revs": L10,
#             "P_kN": P,
#             "C_required_kN": C_required,
#             "p": p,
#             "life_evaluation": self.classify_life_hours(life_hours),
#             "application_evaluation": self.infer_application_from_rpm_and_life(rpm, life_hours),
#         }

#     # --------------------------------------------------
#     # DB search
#     # --------------------------------------------------
#     def run_direct_search(self, entities: Dict[str, Any]):
#         query = supabase.table("bearing_master").select("*")

#         if entities.get("bore_d_mm") is not None:
#             query = query.eq("Bore_diameter", entities["bore_d_mm"])
#         if entities.get("outer_D_mm") is not None:
#             query = query.eq("D", entities["outer_D_mm"])
#         if entities.get("width_B_mm") is not None:
#             query = query.eq("B", entities["width_B_mm"])
#         if entities.get("bearing_type"):
#             query = query.ilike("Category", f"%{entities['bearing_type']}%")
#         if entities.get("brand"):
#             query = query.ilike("Brand", f"%{entities['brand']}%")
#         if entities.get("designation"):
#             code = entities["designation"].replace(" ", "")
#             query = query.ilike("Designation", f"%{code}%")
#         if entities.get("rpm"):
#             query = query.gte("Limiting_speed_oil", entities["rpm"])

#         return query.execute().data

#     def run_engineering_selection(self, entities: Dict[str, Any], calc: Dict[str, Any]):
#         query = (
#             supabase.table("bearing_master")
#             .select("*")
#             .gte("Basic_dynamic_load_rating", calc["C_required_kN"])
#             .gte("Limiting_speed_oil", entities["rpm"])
#         )

#         if entities.get("bore_d_mm") is not None:
#             query = query.eq("Bore_diameter", entities["bore_d_mm"])
#         if entities.get("outer_D_mm") is not None:
#             query = query.eq("D", entities["outer_D_mm"])
#         if entities.get("width_B_mm") is not None:
#             query = query.eq("B", entities["width_B_mm"])

#         return query.execute().data

#     # --------------------------------------------------
#     # Public entry
#     # --------------------------------------------------
#     def run(self, query: str) -> Dict[str, Any]:
#         entities = self.extract_entities(query)
#         intent = self.decide_intent(entities)

#         if intent["intent"] == "DIRECT_SEARCH":
#             return {
#                 "intent": intent,
#                 "entities": entities,
#                 "results": self.run_direct_search(entities),
#             }

#         if entities.get("application_hint"):
#             defaults = self.derive_defaults_from_application(entities["application_hint"])
#             if defaults:
#                 for k, v in defaults.items():
#                     if entities.get(k) is None:
#                         entities[k] = v

#         calc = self.compute_engineering_requirements(entities)
#         results = self.run_engineering_selection(entities, calc)

#         return {
#             "intent": intent,
#             "entities": entities,
#             "engineering": calc,
#             "results": results,
#         }



from typing import Any, Dict, Optional
import json
from mistralai import Mistral
# from groq import Groq
from app.supabase_client import supabase
from app.settings import MISTRAL_API_KEY, ENTITY_EXTRACT_SYSTEM_PROMPT


class KyvoEngine:
    def __init__(self):
        self.mistral_client = Mistral(api_key=MISTRAL_API_KEY)

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------
    def safe_json_load(self, s: str) -> Dict[str, Any]:
        s = s.strip()
        try:
            return json.loads(s)
        except Exception:
            if "{" in s and "}" in s:
                s = s[s.index("{"): s.rindex("}") + 1]
                return json.loads(s)
            raise

    # --------------------------------------------------
    # Entity extraction
    # --------------------------------------------------
    def extract_entities(self, user_query: str) -> Dict[str, Any]:
        resp = self.mistral_client.chat.complete(
            model="mistral-medium-latest",
            messages=[
                {"role": "system", "content": ENTITY_EXTRACT_SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ],
            temperature=0.0,
        )

        content = resp.choices[0].message.content
        data = self.safe_json_load(content)

        template = {
            "bore_d_mm": None,
            "outer_D_mm": None,
            "width_B_mm": None,
            "life_hours": None,
            "rpm": None,
            "radial_load_kN": None,
            "axial_load_kN": None,
            "bearing_type": None,
            "brand": None,
            "designation": None,
            "application_hint": None,
        }

        for k in template:
            if k not in data:
                data[k] = None

        return data

    # --------------------------------------------------
    # Intent
    # --------------------------------------------------
    def decide_intent(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        life = entities.get("life_hours")
        radial = entities.get("radial_load_kN")
        application_hint = entities.get("application_hint")

        if life is not None or radial is not None:
            return {
                "intent": "ENGINEERING_SELECTION",
                "missing_fields": [],
                "reason": "Life or load specified → engineering calculation required."
            }

        if application_hint is not None:
            return {
                "intent": "ENGINEERING_SELECTION",
                "missing_fields": [],
                "reason": "Application-based request → derive engineering parameters."
            }

        return {
            "intent": "DIRECT_SEARCH",
            "missing_fields": [],
            "reason": "No engineering or application requirement → direct catalogue search."
        }



    


    # --------------------------------------------------
    # Defaults from application
    # --------------------------------------------------
    def normalize_application_hint(self, s: str) -> str:
        return (
        s.lower()
         .strip()
         .replace("-", " ")
         .replace("_", " ")
    )


    def derive_defaults_from_application(self, application_hint: str):
        ah = self.normalize_application_hint(application_hint)

        # list of (keywords, defaults)
        mapping = [
            (["slewing", "slewing ring", "turntable", "yaw drive", "excavator", "rotary table"],
            {"life_hours": 12000, "rpm": 50, "radial_load_kN": 30.0, "axial_load_kN": 10.0}),
            (["conveyor", "crusher", "cement mill", "rolling mill", "paper dryer", "large pump"],
            {"life_hours": 8000, "rpm": 300, "radial_load_kN": 10.0, "axial_load_kN": 0.0}),
            (["gearbox", "gearboxes", "industrial pump", "fan", "low speed motor", "compressor", "rubber mixer"],
            {"life_hours": 8000, "rpm": 1500, "radial_load_kN": 8.0, "axial_load_kN": 2.0}),
            (["automotive wheel", "propeller shaft", "engine", "rocker arm", "reducer", "machinery spindle"],
            {"life_hours": 6000, "rpm": 3000, "radial_load_kN": 6.0, "axial_load_kN": 1.5}),
            (["household", "household appliance", "small motor", "blower", "light rolling mill", "automotive transmission"],
            {"life_hours": 3000, "rpm": 7000, "radial_load_kN": 2.0, "axial_load_kN": 0.5}),
            (["machine tool spindle", "turbocharger", "high speed pump", "dental drill", "small turbine"],
            {"life_hours": 2000, "rpm": 15000, "radial_load_kN": 1.5, "axial_load_kN": 0.5}),
            (["air compressor", "high performance motor", "precision grinder", "textile spindle"],
            {"life_hours": 1500, "rpm": 25000, "radial_load_kN": 1.0, "axial_load_kN": 0.3}),
            (["gas turbine", "aerospace", "high speed spindle", "gyroscope"],
            {"life_hours": 1000, "rpm": 60000, "radial_load_kN": 0.5, "axial_load_kN": 0.2}),
            (["ultra high speed", "advanced turbine", "laboratory equipment"],
            {"life_hours": 500, "rpm": 120000, "radial_load_kN": 0.2, "axial_load_kN": 0.1}),
        ]

        for keywords, defaults in mapping:
            if any(keyword in ah for keyword in keywords):
                return defaults

        # fallback: return minimal defaults to prevent crash
        return {"life_hours": 3000, "rpm": 1000, "radial_load_kN": 1.0, "axial_load_kN": 0.0}

    # --------------------------------------------------
    # Life + application inference
    # --------------------------------------------------
    def classify_life_hours(self, life_hours: float):
        if life_hours < 300:
            return {"life_class": "very_low", "life_comment": "Very short specification life"}
        elif 300 <= life_hours <= 3000:
            return {"life_class": "light_duty", "life_comment": "Typical for household, agricultural, or medical equipment"}
        elif 3000 < life_hours <= 8000:
            return {"life_class": "intermittent_industrial", "life_comment": "Typical for intermittent industrial or construction machinery"}
        elif 8000 < life_hours <= 12000:
            return {"life_class": "high_reliability", "life_comment": "High reliability application such as lifts or cranes"}
        else:
            return {"life_class": "very_high_reliability", "life_comment": "Very high life expectation; conservative bearing selection required"}

    def infer_application_from_rpm_and_life(self, rpm: float, life_hours: float):
        if rpm < 100:
            return {"application_class": "slewing_positioning", "examples": ["slewing drives", "positioning systems"]}
        elif 100 <= rpm <= 500:
            return {"application_class": "low_speed_industrial", "examples": ["conveyors", "crushers"]}
        elif 500 < rpm <= 2000:
            if life_hours > 8000:
                return {"application_class": "high_reliability_industrial", "examples": ["gearboxes", "pumps", "continuous-duty machinery"]}
            return {"application_class": "general_industrial", "examples": ["gearboxes", "pumps"]}
        elif 2000 < rpm <= 5000:
            return {"application_class": "automotive", "examples": ["automotive systems"]}
        elif 5000 < rpm <= 10000:
            return {"application_class": "small_motors", "examples": ["electric motors", "household machines"]}
        else:
            return {"application_class": "high_speed", "examples": ["spindles", "turbomachinery"]}

    # --------------------------------------------------
    # Engineering
    # --------------------------------------------------
    def compute_engineering_requirements(self, entities: Dict[str, Any], category_hint: Optional[str] = None):
        life_hours = entities["life_hours"]
        rpm = entities["rpm"]
        Fr = entities["radial_load_kN"]
        Fa = entities.get("axial_load_kN") or 0.0

        L10 = (life_hours * 60 * rpm) / 1_000_000
        P = Fr + Fa

        p = 10 / 3
        if category_hint and "ball" in category_hint.lower():
            p = 3

        C_required = P * (L10 ** (1 / p))

        return {
            "L10_million_revs": L10,
            "P_kN": P,
            "C_required_kN": C_required,
            "p": p,
            "life_evaluation": self.classify_life_hours(life_hours),
            "application_evaluation": self.infer_application_from_rpm_and_life(rpm, life_hours),
        }

    # --------------------------------------------------
    # DB search
    # --------------------------------------------------
    def run_direct_search(self, entities: Dict[str, Any]):
        query = supabase.table("bearing_master").select("*")

        if entities.get("bore_d_mm") is not None:
            query = query.eq("Bore_diameter", entities["bore_d_mm"])
        if entities.get("outer_D_mm") is not None:
            query = query.eq("D", entities["outer_D_mm"])
        if entities.get("width_B_mm") is not None:
            query = query.eq("B", entities["width_B_mm"])
        if entities.get("bearing_type"):
            query = query.ilike("Category", f"%{entities['bearing_type']}%")
        if entities.get("brand"):
            query = query.ilike("Brand", f"%{entities['brand']}%")
        if entities.get("designation"):
            code = entities["designation"].replace(" ", "")
            query = query.ilike("Designation", f"%{code}%")
        if entities.get("rpm"):
            query = query.gte("Limiting_speed_oil", entities["rpm"])

        return query.execute().data

    def run_engineering_selection(self, entities: Dict[str, Any], calc: Dict[str, Any]):
        query = (
            supabase.table("bearing_master")
            .select("*")
            .gte("Basic_dynamic_load_rating", calc["C_required_kN"])
            .gte("Limiting_speed_oil", entities["rpm"])
        )

        if entities.get("bore_d_mm") is not None:
            query = query.eq("Bore_diameter", entities["bore_d_mm"])
        if entities.get("outer_D_mm") is not None:
            query = query.eq("D", entities["outer_D_mm"])
        if entities.get("width_B_mm") is not None:
            query = query.eq("B", entities["width_B_mm"])

        return query.execute().data

    # --------------------------------------------------
    # Public entry
    # --------------------------------------------------
    def run(self, query: str) -> Dict[str, Any]:
        entities = self.extract_entities(query)
        intent = self.decide_intent(entities)

        if intent["intent"] == "DIRECT_SEARCH":
            return {
                "intent": intent,
                "entities": entities,
                "results": self.run_direct_search(entities),
            }

        if entities.get("application_hint") and (entities.get("life_hours") is None or entities.get("rpm") is None):
            defaults = self.derive_defaults_from_application(entities["application_hint"])
            if defaults:
                for k, v in defaults.items():
                    if entities.get(k) is None:
                        entities[k] = v


        calc = self.compute_engineering_requirements(entities)
        results = self.run_engineering_selection(entities, calc)

        return {
            "intent": intent,
            "entities": entities,
            "engineering": calc,
            "results": results,
        }
