import pandas as pd
import streamlit as st
from celery.result import AsyncResult
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

from utils.flower_client import FlowerClient
from worker.celery import create_task

# from st_aggrid.grid_options_builder import GridOptionsBuilder


st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)
st.write("# Streamlit+Celery+Flower POC! 👋")

st.sidebar.success("Select a demo above.")

with st.form("my_form"):
    st.header("Create a Celery Task")
    index = st.number_input("Time iifn Second", min_value=0,
                            max_value=100, key="index")
    if st.form_submit_button("Submit"):
        st.write(f"Submitted Tasks: {create_task.delay(index)}")


fc = FlowerClient()

# create_task(10)
# resp = requests.get('http://localhost:5555/api/tasks')
# option = st.selectbox(
#     'How would you like to be contacted?',
#     ('Email', 'Home phone', 'Mobile phone'))

# st.write('You selected:', option)
# ci = app.control.inspect()
# st.write(ci.stats())
# st.write(dir(ci))

st.header("Celery Task list")
(
    page_col,
    page_size_col,
    taskname_col,
    state_col,
    sort_by_col,
    asc_col
    # received_start_col,
    # received_end_col
) = st.columns(6)
with page_col:
    page = st.number_input(
        "Page", min_value=1, key="page")

with page_size_col:
    page_size = st.number_input(
        "Page Size", min_value=10, max_value=50, key="page_size")

with sort_by_col:

    sort_by = st.selectbox(
        'Sort By', ("", "name", "state", "received", "started"), key="sort_by"

    )

with taskname_col:
    taskname = st.selectbox(
        'Task Name', ["", *fc.get_task_type()], key="taskname"
    )
with state_col:
    state = st.selectbox(
        'State', ("", "SUCCESS", "STARTED", "FAILURE"), key="state"
    )
with asc_col:
    is_asc = st.selectbox(
        'Order by Asc', (True, False), key="is_asc"
    )
# with received_start_col:
#     received_start = st.number_input(
#         "Start Time", min_value=10, max_value=100, key="received_start")
# with received_end_col:
#     received_end = st.number_input(
#         "End Time", min_value=10, max_value=100, key="received_end")

# with st.form("my_form"):
#     if st.form_submit_button("Submit"):
celery_tasks = fc.get_tasks(
    page=page,
    page_size=page_size,
    taskname=taskname,
    state=state,
    sort_field=sort_by,
    order_type=is_asc
)

df = df1 = pd.DataFrame(celery_tasks)
if not df.empty:
    # df['timestamp'] = pd.to_datetime(df['timestamp'],  unit='s')
    # df['failed'] = pd.to_datetime(df['failed'],  unit='s')
    # df['succeeded'] = pd.to_datetime(df['succeeded'],  unit='s')
    # df['started'] = pd.to_datetime(df['started'],  unit='s')
    # df['received'] = pd.to_datetime(df['received'],  unit='s')
    df1 = df[["uuid", "name", "state", "received", "started",
              "succeeded", "failed", "timestamp", "runtime"]]

st.header("Dataframe")
st.dataframe(df)

js_element = JsCode(
    """
    class DetailCellRenderer {
        init(params) {
            this.params = params;
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
            <div style="position:relative;height:100%;width:100%;padding:5px;">
              <div style="float:left;padding:5px;margin:5px;width:150px;">
                ${this.getTemplate()}
              </div>
            </div>
            `; 
        }

        getTemplate() {
            let data = this.params.data;
            let template = '';
            for (let item in data) {
                template += `
                <div style="padding-top: 4px;">
                    <b>${this.titleCase(item)}: </b> 
                    ${data[item]}
                </div>`;
            };
            return template
        }

        titleCase(str) {
            return str.toLowerCase().split(' ').map(function(word) {
                return word.replace(word[0], word[0].toUpperCase());
            }).join(' ');
        }

        getGui() {
            return this.eGui;
        }

        refresh(params) {
            return false;
        }
    }
    """
)

st.header("AG Grid")
if not df.empty:
    gridOptions = {
        # enable Master / Detail
        "masterDetail": True,
        "rowSelection": "multiple",
        # "detailRowHeight": 700,
        # "detailCellRenderer": js_element,
        # the first Column is configured to use agGroupCellRenderer
        "columnDefs": [
            {
                "field": "name",
                "cellRenderer": "agGroupCellRenderer",
                "checkboxSelection": True,
            },
            {"field": "uuid"},
            {"field": "state"},
            {"field": "timestamp",
                "valueFormatter": "x ? new Date(x * 1000) : 'NA'"},
            {"field": "runtime", "valueFormatter": "x.toLocaleString() + 's'"}

            # {"field": "minutes", "valueFormatter": "x.toLocaleString() + 'm'"},
        ],
        # "defaultColDef": {
        #     "flex": 1,
        # },
        # provide Detail Cell Renderer Params

        "detailCellRendererParams": {
            # provide the Grid Options to use on the Detail Grid
            "detailGridOptions": {
                # "rowSelection": "single",
                "suppressRowClickSelection": True,
                "columnDefs": [
                    {"field": "result", "minWidth": 150},
                    {"field": "args"},
                    {"field": "kwargs"},
                    {"field": "received",
                        "valueFormatter": "x ? new Date(x * 1000) : 'NA'"},
                    {"field": "started",
                        "valueFormatter": "x ? new Date(x * 1000) : 'NA'"},
                    {"field": "succeeded",
                        "valueFormatter": "x ? new Date(x * 1000) : 'NA'"},
                    {"field": "failed",
                     "valueFormatter": "x ? new Date(x * 1000) : 'NA'"},
                    {"field": "exception"},
                    {"field": "traceback"},
                ],
                # "defaultColDef": {
                #     # "sortable": True,
                #     "flex": 1,
                # },
            },
            # get the rows for each Detail Grid
            "getDetailRowData": JsCode(
                """function (params) {
                    console.log(params);
                    params.successCallback([params.data]);
                }"""
            ).js_code,
        },
    }
    grid_table = AgGrid(
        df,
        height=500,
        gridOptions=gridOptions,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED
    )

    if selected_rows := grid_table["selected_rows"]:
        st.header("Selected Row/s")
        detail_table = AgGrid(pd.DataFrame(selected_rows))
        # st.table(selected_rows)
        # st.header("Detail Selected Task")
        # st.write(fc.get_task(selected_rows[0]["uuid"]))
        # task_id = selected_rows[0]["uuid"]

    # task_result = AsyncResult(task_id)
    # result = {
    #     "task_id": task_id,
    #     # "task_status": task_result.status,
    #     "task_result": task_result.result
    # }
    # st.write(result)
# else:

st.json(st.session_state)
