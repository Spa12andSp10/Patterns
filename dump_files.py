from Src.Logics.storage_manager import storage_manager
from Src.Logics.settings_manager import settings_manager

sm = settings_manager()
sm.load("Tst/settings.json")
sm.settings.first_launch_flag = False
sm.save()
sm.save_settings("out_settings.json")

st = storage_manager()
st.load("Tst/storage_data.json")
st.save("out_storage_raw.json")
st.save_models("out_storage_models.json")