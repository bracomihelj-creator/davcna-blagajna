"""Vizualni designer postavitve polj Minimax knjižbe — klik celice ali povleci."""

from __future__ import annotations

import copy
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional, Tuple

from v2.kirkpr_knjizba_form_layout import knjizba_form_catalog_for_book

ENTRY_WIDTH_MIN = 8
ENTRY_WIDTH_MAX = 80
DRAG_THRESHOLD_PX = 4


class KnjizbaFormDesigner(ttk.Frame):
    """Mreža polj — klik prazne celice ali povleci polje v stolpec 0 / 1."""

    CELL_W = 300
    CELL_H = 40
    PAD = 6
    HEADER_H = 28
    DEFAULT_CANVAS_H = 380

    def __init__(
        self,
        master: tk.Misc,
        *,
        get_book: Callable[[], str],
        get_columns: Callable[[], int],
        get_fields: Callable[[], List[Dict[str, Any]]],
        set_fields: Callable[[List[Dict[str, Any]]], None],
        get_entry_width: Callable[[], int],
        on_changed: Optional[Callable[[], None]] = None,
        on_select: Optional[Callable[[Optional[str]], None]] = None,
    ) -> None:
        super().__init__(master)
        self._get_book = get_book
        self._get_columns = get_columns
        self._get_fields = get_fields
        self._set_fields = set_fields
        self._get_entry_width = get_entry_width
        self._on_changed = on_changed
        self._on_select = on_select

        self._pending_key: Optional[str] = None
        self._drag_key: Optional[str] = None
        self._drag_active = False
        self._press_xy = (0.0, 0.0)
        self._drag_offset = (0.0, 0.0)
        self._chip_size: Tuple[float, float] = (0.0, 0.0)
        self._selected_key: Optional[str] = None
        self._canvas_h = self.DEFAULT_CANVAS_H
        self._chip_rects: Dict[str, int] = {}
        self._chip_texts: Dict[str, int] = {}
        self._slot_items: Dict[Tuple[int, int], int] = {}
        self._layout_slots: List[Tuple[int, int, int, int, int, int]] = []
        self._placed_items: Dict[str, Dict[str, Any]] = {}
        self._catalog: Dict[str, Tuple[str, str]] = {}

        top = ttk.Frame(self)
        top.pack(fill="x", pady=(0, 4))
        ttk.Label(
            top,
            text=(
                "Klik polje = izberi. Klik rumene celice = premakni izbrano polje tja. "
                "Ali povleci polje. Stolpec 0 = levo, 1 = desno."
            ),
            foreground="#555555",
            wraplength=620,
        ).pack(side="left", fill="x", expand=True)

        tools = ttk.Frame(top)
        tools.pack(side="right")
        ttk.Button(tools, text="← Stol. 0", width=8, command=lambda: self._nudge_column(0)).pack(
            side="left", padx=(0, 2)
        )
        ttk.Button(tools, text="Stol. 1 →", width=8, command=lambda: self._nudge_column(1)).pack(
            side="left", padx=(0, 6)
        )
        ttk.Label(tools, text="Višina:").pack(side="left", padx=(0, 4))
        ttk.Button(tools, text="−", width=3, command=lambda: self._adjust_canvas_height(-40)).pack(
            side="left", padx=(0, 2)
        )
        ttk.Button(tools, text="+", width=3, command=lambda: self._adjust_canvas_height(40)).pack(
            side="left", padx=(0, 8)
        )
        ttk.Button(tools, text="Osveži", command=self.refresh).pack(side="left")

        self._sel_var = tk.StringVar(value="Ni izbranega polja")
        ttk.Label(self, textvariable=self._sel_var, foreground="#333333").pack(anchor="w", pady=(0, 2))

        self._canvas = tk.Canvas(
            self,
            height=self._canvas_h,
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        vsb = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=vsb.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        self._canvas.bind("<Double-Button-1>", self._on_double_click)
        self._canvas.bind("<ButtonPress-1>", self._on_canvas_press, add="+")
        self._canvas.bind("<B1-Motion>", self._on_canvas_motion, add="+")
        self._canvas.bind("<ButtonRelease-1>", self._on_canvas_release, add="+")

    def _columns(self) -> int:
        return max(1, min(2, int(self._get_columns() or 1)))

    def _adjust_canvas_height(self, delta: int) -> None:
        self._canvas_h = max(160, min(720, self._canvas_h + delta))
        self._canvas.configure(height=self._canvas_h)

    def _effective_entry_width(self, item: Dict[str, Any]) -> int:
        try:
            custom = int(item.get("entry_width") or 0)
        except (TypeError, ValueError):
            custom = 0
        if custom > 0:
            return max(ENTRY_WIDTH_MIN, min(ENTRY_WIDTH_MAX, custom))
        return max(ENTRY_WIDTH_MIN, min(ENTRY_WIDTH_MAX, int(self._get_entry_width() or 48)))

    def _notify_changed(self) -> None:
        if self._on_changed:
            self._on_changed()

    def selected_key(self) -> Optional[str]:
        return self._selected_key

    def _select_key(self, key: Optional[str], *, notify: bool = True) -> None:
        self._selected_key = key
        if key and key in self._catalog:
            item = self._placed_items.get(key, {})
            title = self._catalog[key][0]
            ew = self._effective_entry_width(item)
            row = int(item.get("row", -1) or -1)
            col = int(item.get("col", -1) or -1)
            pos = ""
            if row >= 0:
                pos = f" | vrstica {row}"
                if self._columns() == 2 and col in (0, 1):
                    pos += f", stolpec {col}"
            self._sel_var.set(f"Izbrano: {title}  [{ew}]{pos}")
        else:
            self._sel_var.set("Ni izbranega polja — klikni polje ali celico")
        if notify and self._on_select:
            self._on_select(key)

    def _slot_at_point(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        for row, col, x1, y1, x2, y2 in reversed(self._layout_slots):
            if x1 <= x <= x2 and y1 <= y <= y2:
                return row, col
        return None

    def _chip_key_at(self, cx: float, cy: float) -> Optional[str]:
        for iid in reversed(self._canvas.find_overlapping(cx, cy, cx, cy)):
            for tag in self._canvas.gettags(iid):
                if tag.startswith("chip:"):
                    return tag.split(":", 1)[1]
        return None

    def _normalize_field_position(
        self, item: Dict[str, Any], *, columns: int
    ) -> Optional[Tuple[int, int]]:
        row = int(item.get("row", -1) or -1)
        if row < 0:
            return None
        if columns == 1:
            item["col"] = -1
            return row, 0
        col = int(item.get("col", -1) or -1)
        if col not in (0, 1):
            col = 0
            item["col"] = 0
        return row, col

    def _build_placed_map(
        self, fields: List[Dict[str, Any]], columns: int
    ) -> Dict[Tuple[int, int], Dict[str, Any]]:
        placed: Dict[Tuple[int, int], Dict[str, Any]] = {}
        pending: List[Dict[str, Any]] = []

        for item in fields:
            key = str(item.get("key") or "")
            if key not in self._catalog:
                continue
            pos = self._normalize_field_position(item, columns=columns)
            if pos is None:
                pending.append(item)
                continue
            if pos not in placed:
                placed[pos] = item
            else:
                item["row"] = -1
                item["col"] = -1
                pending.append(item)

        auto_idx = 0
        for item in pending:
            while True:
                r = auto_idx // columns
                c = auto_idx % columns
                auto_idx += 1
                if (r, c) not in placed:
                    placed[(r, c)] = item
                    item["row"] = r
                    item["col"] = c if columns == 2 else -1
                    break

        return placed

    def _field_at_slot(
        self, fields: List[Dict[str, Any]], row: int, col: int, *, columns: int
    ) -> Optional[Dict[str, Any]]:
        for f in fields:
            if str(f.get("key") or "") not in self._catalog:
                continue
            pos = self._normalize_field_position(f, columns=columns)
            if pos == (row, col):
                return f
        return None

    def _move_field_to_slot(
        self,
        drag_key: str,
        target_row: int,
        target_col: int,
        *,
        notify: bool = True,
    ) -> bool:
        columns = self._columns()
        if columns == 1:
            target_col = 0

        fields = [copy.deepcopy(f) for f in self._get_fields()]
        moving = next((f for f in fields if str(f.get("key")) == drag_key), None)
        if moving is None:
            return False

        occupant = self._field_at_slot(fields, target_row, target_col, columns=columns)
        old_pos = self._normalize_field_position(moving, columns=columns)
        old_row = old_pos[0] if old_pos else -1
        old_col = old_pos[1] if old_pos else 0

        if occupant is not None and str(occupant.get("key")) != drag_key:
            occupant["row"] = old_row if old_row >= 0 else target_row
            if columns == 2:
                occupant["col"] = old_col if old_col in (0, 1) else target_col
            else:
                occupant["col"] = -1

        moving["row"] = target_row
        moving["col"] = target_col if columns == 2 else -1

        self._set_fields(fields)
        self._selected_key = drag_key
        self.refresh()
        if notify:
            self._notify_changed()
        return True

    def _nudge_column(self, col: int) -> None:
        key = self._selected_key
        if not key or self._columns() != 2:
            self._sel_var.set("Izberi polje in nastavi 2 stolpca v «Okno in mreža».")
            return
        fields = [copy.deepcopy(f) for f in self._get_fields()]
        item = next((f for f in fields if str(f.get("key")) == key), None)
        if item is None:
            return
        row = int(item.get("row", -1) or -1)
        if row < 0:
            row = 0
        self._set_fields(fields)
        self._move_field_to_slot(key, row, col)

    def refresh(self) -> None:
        if self._drag_key or self._pending_key:
            return

        self._canvas.delete("all")
        self._chip_rects.clear()
        self._chip_texts.clear()
        self._slot_items.clear()
        self._layout_slots.clear()
        self._placed_items.clear()

        book = (self._get_book() or "KIR").strip().upper()
        self._catalog = knjizba_form_catalog_for_book(book)
        columns = self._columns()
        fields = [copy.deepcopy(f) for f in self._get_fields()]

        placed = self._build_placed_map(fields, columns)
        self._set_fields(fields)

        max_row = max((r for r, _c in placed), default=-1)
        for row in range(max_row + 3):
            for col in range(columns):
                x1 = self.PAD + col * (self.CELL_W + self.PAD)
                y1 = self.PAD + self.HEADER_H + row * (self.CELL_H + self.PAD)
                x2 = x1 + self.CELL_W
                y2 = y1 + self.CELL_H
                self._layout_slots.append((row, col, x1, y1, x2, y2))
                slot_id = self._canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    outline="#e0e0e0",
                    fill="#fafafa",
                    dash=(3, 3),
                    tags=(f"slot:{row}:{col}", "slot"),
                )
                self._slot_items[(row, col)] = slot_id
                self._canvas.create_text(
                    x1 + 6,
                    y1 + 4,
                    anchor="nw",
                    text=f"{row},{col}",
                    fill="#bbbbbb",
                    font=("Segoe UI", 7),
                    tags=("slot_label", f"slot:{row}:{col}"),
                )

        for (row, col), item in sorted(placed.items()):
            key = str(item.get("key") or "")
            self._placed_items[key] = item
            self._draw_chip(item, self._catalog, row, col)

        total_h = self.PAD + self.HEADER_H + (max_row + 4) * (self.CELL_H + self.PAD)
        total_w = columns * (self.CELL_W + self.PAD) + self.PAD
        self._canvas.configure(scrollregion=(0, 0, total_w, total_h))
        self._canvas.create_text(
            self.PAD,
            6,
            anchor="nw",
            text=f"Vizualni razpored — {book} ({columns} stolpec/stolpca)",
            fill="#333333",
            font=("Segoe UI", 9, "bold"),
        )

        if self._selected_key and self._selected_key in self._placed_items:
            self._select_key(self._selected_key, notify=False)
        else:
            self._select_key(None, notify=False)

    def _chip_label(self, item: Dict[str, Any], catalog: Dict[str, Tuple[str, str]]) -> str:
        key = str(item.get("key") or "")
        custom = str(item.get("label") or "").strip()
        default = catalog.get(key, (key, ""))[0]
        title = custom or default
        vis = "✓" if bool(item.get("visible", True)) else "○"
        ew = self._effective_entry_width(item)
        row = int(item.get("row", -1) or -1)
        col = int(item.get("col", -1) or -1)
        pos = f" r{row}c{col}" if row >= 0 and self._columns() == 2 else ""
        return f"{vis} {title}{pos}  [{ew}]"

    def _slot_rect(self, row: int, col: int) -> Tuple[float, float, float, float]:
        slot = next((s for s in self._layout_slots if s[0] == row and s[1] == col), None)
        if slot is None:
            return 0.0, 0.0, 0.0, 0.0
        _r, _c, x1, y1, x2, y2 = slot
        return x1 + 4, y1 + 4, x2 - 4, y2 - 4

    def _draw_chip(
        self,
        item: Dict[str, Any],
        catalog: Dict[str, Tuple[str, str]],
        row: int,
        col: int,
    ) -> None:
        key = str(item.get("key") or "")
        cx1, cy1, cx2, cy2 = self._slot_rect(row, col)
        if cx2 <= cx1:
            return
        visible = bool(item.get("visible", True))
        selected = key == self._selected_key
        fill = "#d4ebfa" if selected else ("#e8f4fc" if visible else "#f0f0f0")
        outline = "#1a6fb5" if selected else ("#4a90c4" if visible else "#aaaaaa")
        tag = f"chip:{key}"

        rect = self._canvas.create_rectangle(
            cx1, cy1, cx2, cy2, fill=fill, outline=outline, width=2, tags=("chip", tag)
        )
        text = self._canvas.create_text(
            cx1 + 6,
            (cy1 + cy2) // 2,
            anchor="w",
            text=self._chip_label(item, catalog),
            fill="#222222" if visible else "#888888",
            tags=("chip", tag),
        )
        self._chip_rects[key] = rect
        self._chip_texts[key] = text

    def _highlight_slot(self, slot: Optional[Tuple[int, int]]) -> None:
        for (row, col), iid in self._slot_items.items():
            self._canvas.itemconfigure(iid, fill="#fff8dc" if slot == (row, col) else "#fafafa")

    def _slot_for_chip(self, key: str) -> Optional[Tuple[int, int]]:
        rect_id = self._chip_rects.get(key)
        if rect_id is None:
            return None
        bbox = self._canvas.bbox(rect_id)
        if not bbox:
            return None
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        return self._slot_at_point(cx, cy)

    def _on_canvas_press(self, event: tk.Event) -> None:
        cx, cy = self._canvas.canvasx(event.x), self._canvas.canvasy(event.y)
        key = self._chip_key_at(cx, cy)
        if key:
            self._pending_key = key
            self._press_xy = (cx, cy)
            self._drag_active = False
            self._select_key(key)
            return

        self._pending_key = None
        slot = self._slot_at_point(cx, cy)
        if slot and self._selected_key:
            self._move_field_to_slot(self._selected_key, slot[0], slot[1])
            return
        if slot:
            self._sel_var.set(
                f"Celica {slot[0]},{slot[1]} — najprej izberi polje, nato klikni celico."
            )

    def _on_canvas_motion(self, event: tk.Event) -> None:
        if not self._pending_key and not self._drag_key:
            return
        cx, cy = self._canvas.canvasx(event.x), self._canvas.canvasy(event.y)
        key = self._drag_key or self._pending_key
        if not key or key not in self._chip_rects:
            return

        if not self._drag_active:
            dx = abs(cx - self._press_xy[0])
            dy = abs(cy - self._press_xy[1])
            if dx < DRAG_THRESHOLD_PX and dy < DRAG_THRESHOLD_PX:
                slot = self._slot_at_point(cx, cy)
                self._highlight_slot(slot)
                return
            self._drag_active = True
            self._drag_key = key
            bbox = self._canvas.bbox(self._chip_rects[key])
            if bbox:
                self._drag_offset = (cx - bbox[0], cy - bbox[1])
                self._chip_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            self._canvas.tag_raise(self._chip_rects[key])
            self._canvas.tag_raise(self._chip_texts[key])

        w, h = self._chip_size
        x = cx - self._drag_offset[0]
        y = cy - self._drag_offset[1]
        self._canvas.coords(self._chip_rects[key], x, y, x + w, y + h)
        self._canvas.coords(self._chip_texts[key], x + 6, y + h // 2)
        self._highlight_slot(self._slot_for_chip(key) or self._slot_at_point(cx, cy))

    def _on_canvas_release(self, event: tk.Event) -> None:
        cx, cy = self._canvas.canvasx(event.x), self._canvas.canvasy(event.y)
        self._pending_key = None
        dragged = self._drag_active and self._drag_key is not None
        drag_key = self._drag_key
        self._drag_active = False
        self._drag_key = None
        self._highlight_slot(None)

        if not dragged or not drag_key:
            return

        slot = self._slot_for_chip(drag_key) or self._slot_at_point(cx, cy)
        if slot is None:
            self._sel_var.set("Spusti v rumeno celico (oznaka n,n zgoraj levo).")
            self.refresh()
            return

        self._move_field_to_slot(drag_key, slot[0], slot[1])

    def _on_double_click(self, event: tk.Event) -> None:
        cx, cy = self._canvas.canvasx(event.x), self._canvas.canvasy(event.y)
        key = self._chip_key_at(cx, cy)
        if not key:
            return
        fields = [copy.deepcopy(f) for f in self._get_fields()]
        item = next((f for f in fields if str(f.get("key")) == key), None)
        if item is None:
            return
        item["visible"] = not bool(item.get("visible", True))
        self._set_fields(fields)
        self.refresh()
        self._notify_changed()
