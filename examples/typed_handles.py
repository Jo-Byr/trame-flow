from pathlib import Path
from typing import Any

from trame.app import TrameApp
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import client
from trame.widgets.html import Div, Span
from trame.widgets.vuetify3 import (
    Template,
    VBtn,
    VDivider,
    VIcon,
    VRow,
    VSelect,
    VSpacer,
    VTextField,
)
from trame_flow.module.core import create_node
from trame_flow.widgets.flow import (
    Background,
    Controls,
    CustomNode,
    Handle,
    NodeEditor,
)


class Example(TrameApp):
    def __init__(self, server=None):
        super().__init__(server)
        self.next_node_id = 0

        self.state.x = 0
        self.state.y = 0
        self.int_color = "#83ef44"
        self.str_color = "#e03bf6"
        self._handle_counter = 0
        self.ui = self.build_ui()

    @property
    def state(self):
        return self.server.state

    def add_node(self):
        self.vueflow.add_node(
            create_node(
                id=str(self.next_node_id),
                x=0,
                y=0,
                type="dynamic_node",
                label=f"Node {self.next_node_id}",
                data={
                    "in_handles": {},
                    "out_handles": {},
                },
            )
        )
        self.next_node_id += 1

    def set_node_parameter(self, node_id: str, data_key: str, value: Any):
        self.vueflow.update_node(
            node_id,
            data={
                **self.vueflow.get_node(node_id)["data"],
                data_key: value,
            },
        )

    def get_node_parameter(self, node_id, data_key: str) -> Any:
        return self.vueflow.get_node(node_id)["data"].get(data_key, None)

    def add_in_handle(self, node_id: str, handle_type: str):
        node = self.vueflow.get_node(node_id)
        in_handles = node["data"]["in_handles"]
        self.set_node_parameter(
            node_id,
            "in_handles",
            {
                **in_handles,
                f"in-{self._handle_counter} ({handle_type})": handle_type,
            },
        )
        self._handle_counter += 1

    def add_out_handle(self, node_id: str, handle_type: str):
        node = self.vueflow.get_node(node_id)
        out_handles = node["data"]["out_handles"]
        self.set_node_parameter(
            node_id,
            "out_handles",
            {
                **out_handles,
                f"out-{self._handle_counter} ({handle_type})": handle_type,
            },
        )
        self._handle_counter += 1

    def add_handle(self, node_id: str):
        self.set_node_parameter(node_id, "handle_type", None)
        self.set_node_parameter(node_id, "handle_direction", None)
        self.set_node_parameter(node_id, "adding_handle", True)

    def cancel_add_handle(self, node_id: str):
        self.set_node_parameter(node_id, "adding_handle", False)

    def confirm_add_handle(self, node_id: str):
        self.set_node_parameter(node_id, "adding_handle", False)
        handle_type = self.get_node_parameter(node_id, "handle_type")
        if handle_type is None:
            return

        if self.get_node_parameter(node_id, "handle_direction") == "in":
            self.add_in_handle(node_id, handle_type)
        else:
            self.add_out_handle(node_id, handle_type)

    def build_ui(self):
        with SinglePageLayout(self.server) as layout:
            layout.title.set_text("trame-flow example")
            with (
                layout.toolbar,
                VBtn(
                    "Add a node",
                    click=self.add_node,
                ),
            ):
                VIcon("mdi-plus")

            with NodeEditor(
                connection_mode="strict",
                is_valid_connection=(
                    "(connection) => { return nodes[connection.source].data.out_handles[connection.sourceHandle] === nodes[connection.target].data.in_handles[connection.targetHandle]; }",
                ),
            ) as self.vueflow:
                with Path(__file__).with_name("style.css").open() as f:
                    client.Style(f.read())
                Background(gap=10, size=1, pattern_color="#81818a")
                Controls()
                with CustomNode(
                    "dynamic_node",
                    var_name="props",
                ):
                    VTextField(
                        model_value=("props.data.label",),
                        update_modelValue=(
                            self.set_node_parameter,
                            "[props.id, 'label', $event]",
                        ),
                        label="Name",
                        hide_details=True,
                        style="width: 200px;",
                        density="comfortable",
                    )

                    VDivider(style="margin-top: 10px;")

                    left_length_str = "Object.keys(props.data.in_handles).length ?? 0"
                    right_length_str = "Object.keys(props.data.out_handles).length ?? 0"
                    with VRow(
                        v_for=f"(_, i) in Array(Math.max( {left_length_str}, {right_length_str} )).fill()",
                        style="margin: 0; position: relative; height: 24px; align-content: center;",
                    ):
                        with Template(
                            v_if=("Object.keys(props.data.in_handles).length > i",)
                        ):
                            name_str = "`${Object.keys(props.data.in_handles)[i]}`"
                            Span(v_html=(name_str,))
                            Handle(
                                type="target",
                                position="left",
                                connectable=("1",),
                                id=(name_str,),
                                style=(
                                    f"{{ '--vf-handle': Object.values(props.data.in_handles)[i] === 'int' ? '{self.int_color}' : '{self.str_color}' }}",
                                ),
                            )
                        with Template(
                            v_if=("Object.keys(props.data.out_handles).length > i",)
                        ):
                            name_str = "`${Object.keys(props.data.out_handles)[i]}`"
                            VSpacer()
                            Span(v_html=(name_str,))
                            Handle(
                                type="source",
                                position="right",
                                id=(name_str,),
                                style=(
                                    f"{{ '--vf-handle': Object.values(props.data.out_handles)[i] === 'int' ? '{self.int_color}' : '{self.str_color}' }}",
                                ),
                            )

                    VDivider(style="margin-top: 10px;")

                    with VRow(
                        style="margin: 0; margin-top: 10px; justify-content: center;"
                    ):
                        with Div(
                            v_if=("props.data.adding_handle", False),
                            style="display: flex; flex-direction: column; width: 100%;",
                        ):
                            Span("New handle")
                            with VRow(style="margin: 0;"):
                                VSelect(
                                    model_value=("props.data.handle_direction",),
                                    update_modelValue=(
                                        self.set_node_parameter,
                                        "[props.id, 'handle_direction', $event]",
                                    ),
                                    items=(["in", "out"],),
                                    label="In/Out",
                                    hide_details=True,
                                    density="compact",
                                    style="margin: 2px;",
                                )
                            with VRow(style="margin: 0;"):
                                VSelect(
                                    model_value=("props.data.handle_type",),
                                    update_modelValue=(
                                        self.set_node_parameter,
                                        "[props.id, 'handle_type', $event]",
                                    ),
                                    items=(["int", "str"],),
                                    label="Type",
                                    hide_details=True,
                                    density="compact",
                                    style="margin: 2px;",
                                )
                            with VRow(style="margin: 0;"):
                                VBtn(
                                    "Cancel",
                                    click=(self.cancel_add_handle, "[props.id]"),
                                    density="compact",
                                    style="margin: 2px; flex: 1;",
                                )
                                VBtn(
                                    "Ok",
                                    click=(self.confirm_add_handle, "[props.id]"),
                                    density="compact",
                                    style="margin: 2px; flex: 1;",
                                )
                        VBtn(
                            icon="mdi-plus",
                            density="compact",
                            click=(self.add_handle, "[props.id]"),
                            style="margin-right: 5px;",
                            v_else=True,
                        )

                    def on_graph_change(nodes, edges):
                        with self.state:
                            self.state.nodes = nodes
                            self.state.edges = edges
                        self.state.dirty("nodes")
                        self.state.dirty("edges")

            self.vueflow.graph_change = on_graph_change


if __name__ == "__main__":
    app = Example()
    app.server.start()
