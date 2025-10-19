from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from talekeeper.ui.encounter_pane.town_encounter import ShopInterface
from talekeeper.services.shop_service import ShopService, ShopSize


class HexShopInterface(ShopInterface):

    def __init__(self, character_data: Dict[str, Any], settlement_type: str,
                 hex_seed: int, hex_coords: tuple, parent=None,
                 population: Optional[int] = None):
        self.hex_seed = hex_seed
        self.hex_coords = hex_coords
        self.settlement_type = settlement_type

        shop_service = ShopService()
        self.shop_data = shop_service.generate_hex_shop_inventory(
            settlement_type, character_data, hex_seed, population_override=population
        )

        shop_size = self._get_shop_size(settlement_type)

        super().__init__(character_data, shop_size, parent)

        self.shop_inventory = self.shop_data['inventory']
        self.remaining_pool = self.shop_data['actual_pool']

    def _load_shop_inventory(self):
        settlement_name = self._settlement_display_name(self.settlement_type)
        population = self.shop_data.get('population', 0)
        base_cap = self.shop_data.get('base_cap', 0)
        actual_cap = self.shop_data.get('actual_cap', 0)
        cap_variance = self.shop_data.get('cap_variance', 1.0)
        max_item_price = max([item.get('cost_gp', 0) for item in self.shop_data['inventory']]) if self.shop_data['inventory'] else 0
        charisma_roll = self.shop_data['charisma_roll']
        has_crafter = self.shop_data['has_crafter']

        discount = charisma_roll + (20 if has_crafter else 0)
        final_markup = max(0, 25 - discount)
        sell_rate = min(100, 40 + charisma_roll)

        print(f"[Vendor] {settlement_name} (Pop: {population}) | Hex ({self.hex_coords[0]}, {self.hex_coords[1]})")
        print(f"[Vendor] Economic Tier: Base Cap {base_cap} gp × {cap_variance:.0%} = {actual_cap:.0f} gp max")
        print(f"[Vendor] Max Item Price: {max_item_price:.2f} gp | {len(self.shop_data['inventory'])} items in stock")
        print(f"[Vendor] Negotiation Roll: {charisma_roll}{' (+20 Crafter)' if has_crafter else ''}")
        print(f"[Vendor] Buy Markup: {final_markup}% | Sell Rate: {sell_rate}%")
        pass

    def _get_shop_size(self, settlement_type: str) -> ShopSize:
        mapping = {
            'hamlet': ShopSize.SMALL,
            'village': ShopSize.MEDIUM,
            'town_small': ShopSize.LARGE,
            'town_medium': ShopSize.LARGE,
            'town_large': ShopSize.LARGE,
            'empty': ShopSize.SMALL
        }
        return mapping.get(settlement_type, ShopSize.MEDIUM)

    def _add_negotiation_info(self):
        negotiation_text = self._get_negotiation_summary()

        negotiation_label = QLabel(negotiation_text)
        negotiation_label.setObjectName("negotiationInfo")
        negotiation_label.setWordWrap(True)
        negotiation_label.setStyleSheet(
            "background-color: #f0f8ff; "
            "border: 1px solid #4a90e2; "
            "border-radius: 4px; "
            "padding: 8px; "
            "margin: 4px 0px; "
            "color: #1a1a1a;"
        )

        layout = self.layout()
        layout.insertWidget(2, negotiation_label)

    def _get_negotiation_summary(self) -> str:
        charisma_roll = self.shop_data['charisma_roll']
        has_crafter = self.shop_data['has_crafter']
        settlement_name = self._settlement_display_name(self.settlement_type)
        population = self.shop_data.get('population', 0)
        base_cap = self.shop_data.get('base_cap', 0)
        actual_cap = self.shop_data.get('actual_cap', 0)
        cap_variance = self.shop_data.get('cap_variance', 1.0)

        max_item_price = max([item.get('cost_gp', 0) for item in self.shop_data['inventory']]) if self.shop_data['inventory'] else 0
        max_buy_price = max([item.get('buy_price_gp', 0) for item in self.shop_data['inventory']]) if self.shop_data['inventory'] else 0

        discount = charisma_roll + (20 if has_crafter else 0)
        final_markup = max(0, 25 - discount)

        summary = f"Settlement: {settlement_name} (Pop: {population}) | Hex ({self.hex_coords[0]}, {self.hex_coords[1]})\n"
        summary += f"Economic Tier: Base Cap {base_cap} gp × {cap_variance:.0%} = {actual_cap:.0f} gp max\n"
        summary += f"Max Item Price: {max_item_price:.2f} gp (after markup: {max_buy_price:.2f} gp) | {len(self.shop_data['inventory'])} items in stock\n"
        summary += f"Negotiation Roll: {charisma_roll}"

        if has_crafter:
            summary += " (+20 Crafter bonus)"

        summary += f"\nBuy Price Markup: {final_markup}%"

        sell_rate = min(100, 40 + charisma_roll)
        summary += f" | Sell Price Rate: {sell_rate}%"

        return summary

    def _settlement_display_name(self, settlement_type: str) -> str:
        names = {
            'empty': 'Wilderness (no settlement)',
            'hamlet': 'Hamlet',
            'village': 'Village',
            'town_small': 'Small Town',
            'town_medium': 'Medium Town',
            'town_large': 'Large Town'
        }
        return names.get(settlement_type, 'Unknown')

    def _load_character_inventory(self):
        from talekeeper.services.equipment_database import EquipmentDatabase
        equipment_db = EquipmentDatabase()
        shop_service = ShopService()

        all_equipment = equipment_db.get_all_equipment()
        equipment_lookup = {item['name']: item for item in all_equipment}

        try:
            import sqlite3
            conn = sqlite3.connect('talekeeper.db')
            cursor = conn.cursor()

            character_id = self.character_data.get('id')
            cursor.execute('''
                SELECT item_name, item_type, quantity
                FROM character_inventory
                WHERE character_id = ?
            ''', (character_id,))

            inventory_items = cursor.fetchall()
            conn.close()

            self.character_inventory = []
            for item_name, item_type, quantity in inventory_items:
                if item_name in equipment_lookup:
                    item_data = equipment_lookup[item_name].copy()
                    item_data['quantity'] = quantity
                    sell_price_gp, sell_price_display, charisma_roll = shop_service.calculate_sell_price_with_character(
                        item_data.get('cost_gp', 0), self.character_data
                    )
                    item_data['sell_price_gp'] = sell_price_gp
                    item_data['sell_price_display'] = sell_price_display
                    item_data['sell_charisma_roll'] = charisma_roll
                    self.character_inventory.append(item_data)

        except Exception as e:
            print(f"Error loading character inventory: {e}")
            self.character_inventory = []

    def _populate_items_list(self):
        self.items_list.clear()

        if self.shop_mode == "buy":
            items_to_show = self.shop_inventory
            price_key = 'buy_price_display'
        else:
            items_to_show = self.character_inventory
            price_key = 'sell_price_display'

        for item in items_to_show:
            name = item['name']
            price = item[price_key]

            if self.shop_mode == "sell":
                quantity = item.get('quantity', 1)
                from PyQt6.QtWidgets import QListWidgetItem
                item_widget = QListWidgetItem(f"{name} (x{quantity}) - {price} each")
            else:
                from PyQt6.QtWidgets import QListWidgetItem
                item_widget = QListWidgetItem(f"{name} - {price}")

            item_widget.setData(Qt.ItemDataRole.UserRole, item)
            self.items_list.addItem(item_widget)

    def _update_total_cost(self):
        from talekeeper.services.shop_service import format_currency
        current_item = self.items_list.currentItem()
        if current_item:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            quantity = self.quantity_spin.value()

            if self.shop_mode == "buy":
                price_gp = item_data.get('buy_price_gp', item_data.get('shop_price_gp', 0))
                total_gp = price_gp * quantity
                total_display, _ = format_currency(total_gp)
                self.total_cost_label.setText(f"Total Cost: {total_display}")

                if total_gp > self.character_gold:
                    self.total_cost_label.setText(f"Total Cost: {total_display} (Insufficient funds!)")
                    self.purchase_button.setEnabled(False)
                else:
                    self.purchase_button.setEnabled(True)
            else:
                price_gp = item_data.get('sell_price_gp', 0)
                total_gp = price_gp * quantity
                total_display, _ = format_currency(total_gp)
                self.total_cost_label.setText(f"Total Value: {total_display}")
                self.purchase_button.setEnabled(True)

    def _handle_transaction(self):
        from PyQt6.QtWidgets import QMessageBox
        from talekeeper.services.shop_service import format_currency

        current_item = self.items_list.currentItem()
        if not current_item:
            return

        item_data = current_item.data(Qt.ItemDataRole.UserRole)
        quantity = self.quantity_spin.value()
        item_name = item_data['name']

        if self.shop_mode == "buy":
            total_cost_gp = item_data.get('buy_price_gp', item_data.get('shop_price_gp', 0)) * quantity
            total_cost_display, _ = format_currency(total_cost_gp)

            if total_cost_gp > self.character_gold:
                QMessageBox.warning(self, "Insufficient Funds",
                                  f"You need {total_cost_display} but only have {self.character_gold} GP.")
                return

            reply = QMessageBox.question(self, "Confirm Purchase",
                                       f"Purchase {quantity}x {item_name} for {total_cost_display}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self._add_item_to_inventory(item_data, quantity)
                if success:
                    self._deduct_gold(total_cost_gp)
                    self._update_character_gold()
                    self._update_total_cost()
                    QMessageBox.information(self, "Purchase Complete",
                                          f"Successfully purchased {quantity}x {item_name}!")
                else:
                    QMessageBox.critical(self, "Purchase Failed",
                                       "Failed to add item to inventory. Please try again.")
        else:
            shop_service = ShopService()
            sell_price_gp, sell_price_display, charisma_roll = shop_service.calculate_sell_price_with_character(
                item_data.get('cost_gp', 0), self.character_data
            )
            total_value_gp = round(sell_price_gp * quantity, 2)
            total_value_display, _ = format_currency(total_value_gp)

            if total_value_gp > self.remaining_pool:
                max_quantity = int(self.remaining_pool / sell_price_gp)
                pool_display, _ = format_currency(self.remaining_pool)
                if max_quantity == 0:
                    QMessageBox.warning(self, "Vendor Cannot Afford",
                                      f"This vendor only has {pool_display} remaining to spend.\n"
                                      f"They cannot afford even 1x {item_name} ({sell_price_display}).")
                    return
                else:
                    QMessageBox.warning(self, "Vendor Cannot Afford All",
                                      f"This vendor only has {pool_display} remaining to spend.\n"
                                      f"They can only buy {max_quantity}x {item_name}.")
                    return

            reply = QMessageBox.question(self, "Confirm Sale",
                                       f"Sell {quantity}x {item_name} for {total_value_display}?\n"
                                       f"(Negotiation roll: {charisma_roll})\n"
                                       f"Vendor pool remaining after sale: {format_currency(self.remaining_pool - total_value_gp)[0]}",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = self._remove_item_from_inventory(item_data, quantity)
                if success:
                    self._add_gold(total_value_gp)
                    self.remaining_pool -= total_value_gp
                    self._load_character_inventory()
                    self._update_character_gold()
                    self._populate_items_list()
                    QMessageBox.information(self, "Sale Complete",
                                          f"Successfully sold {quantity}x {item_name} for {total_value_display}!")

                    if quantity >= item_data.get('quantity', 1):
                        self.items_list.clearSelection()
                        self.item_details.setText("Select an item to see details")
                        self.purchase_button.setEnabled(False)
                else:
                    QMessageBox.critical(self, "Sale Failed",
                                       "Failed to remove item from inventory. Please try again.")
