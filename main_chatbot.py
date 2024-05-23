from flask import Flask, request, jsonify
import db_helper
import generic_helper
app = Flask(__name__)
inprogress_orders = {}

@app.route("/", methods=['POST'])
def handle_request():
    payload = request.json
    print(payload)  
    intent = payload["queryResult"]["intent"]["displayName"]
    parameters = payload["queryResult"]["parameters"]
    output_contexts = payload["queryResult"]["outputContexts"]

    session_id = generic_helper.extract_session_id(output_contexts[0]["name"])
    intent_handler_dict = {
        "order_add-context:ongoing_order": add_to_order,
        "order_remove - context : ongoing order":remove_from_order,
        "order_complete:context-ongoing order" :complete_order,
        "track_order:context-ongoing_order": track_order
    }
    if intent in intent_handler_dict:
        return intent_handler_dict[intent](parameters , session_id)
    
def remove_from_order(parameters: dict, session_id: str):
    if session_id not in inprogress_orders:
        return jsonify(content={
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
    
    items = parameters["id"]
    current_order = inprogress_orders[session_id]

    removed_items = []
    no_such_items = []

    for item in items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    return jsonify(
         fulfillmentText = fulfillment_text
    )
def add_to_order(parameters: dict , session_id:str):
    product = parameters["item_id"]
    size = parameters["size_chart"]
    product = [item.lstrip('#') for item in product]
    if len(product) != len(size):
        fulfillment_text = "Sorry I am not able to understand what you are trying to convey please write product item and size clearly"
    else:
        new_product_dict = dict(zip(product , size))
        if session_id in inprogress_orders:
            current_product_dict = inprogress_orders[session_id]
            current_product_dict.update(new_product_dict)
            inprogress_orders[session_id] = current_product_dict
        else :
            inprogress_orders[session_id] = new_product_dict
        print("@@@@@@@@@@@@@@@@@@@@@@@@@")
        print(inprogress_orders)
        order_str = generic_helper.get_str_from_product_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far recieved order from your side : {order_str}. Do you need anything else "
    return jsonify(fulfillmentText=fulfillment_text)


def complete_order(parameters:dict, session_id :str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I am having trouble finding the order . Can you please place a new order"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1 :
            fulfillment_text = "Sorry I cannot complete your order due to some order in the backend! "
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome your order has been placed "\
            f"here is your {order_id} : "\
            f"Your total amount of the order is {order_total} which you can pay at the delivery"
        del inprogress_orders[session_id]
    return jsonify(fulfillmentText = fulfillment_text)
def save_to_db(order: dict):
    next_order_id = db_helper.get_next_order_id()
    if next_order_id == -1:
        return -1
    
    for id, size in order.items():
        rcode = db_helper.insert_order_item(id, size, next_order_id)
        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id, "in_progress")
    return next_order_id
   
def track_order(parameters: dict , session_id :str):
    order_id = parameters["number"][0] 
    status = db_helper.get_order_status(order_id)

    if status:
        fulfillment_text = f"The order status for the order id: {order_id} is: {status}"
    else:
        fulfillment_text = f"No order found with the order id: {order_id}"

    return jsonify(fulfillmentText=fulfillment_text)



if __name__ == "__main__":
    app.run(debug=True)