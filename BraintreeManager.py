import braintree
import time
import json

class BraintreeManager:
    def __init__(self, merchant_id, public_key, private_key):
        self.gateway = braintree.BraintreeGateway(
            braintree.Configuration(
                environment=braintree.Environment.Sandbox,
                merchant_id=merchant_id,
                public_key=public_key,
                private_key=private_key
            )
        )

        print(f"Merchant ID: {merchant_id}")

    def get_all_plans(self):
        plans = self.gateway.plan.all()
        return plans

    @staticmethod
    def load_json_data(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    def create_customer(self, customer_data):
        timestamp = str(int(time.time()))

        updated_customer_data = customer_data.copy()
        updated_customer_data['first_name'] += timestamp
        updated_customer_data['last_name'] += timestamp
        updated_customer_data['email'] = f"nemat{timestamp}@example.com"

        result = self.gateway.customer.create(updated_customer_data)
        if result.is_success:
            customer_id = result.customer.id
            payment_token = result.customer.payment_methods[0].token
            return customer_id, payment_token
        return None, None

    def subscribe_customer_to_plan(self, payment_method_token, plan_id):
        result = self.gateway.subscription.create({
            "payment_method_token": payment_method_token,
            "plan_id": plan_id,
        })

        return result.is_success

if __name__ == "__main__":
    gateway_configs = BraintreeManager.load_json_data('config.json')
    customer_data = BraintreeManager.load_json_data('customer_data.json')

    if gateway_configs and customer_data:
        for config in gateway_configs['gateways']:
            braintree_manager = BraintreeManager(
                merchant_id=config["merchant_id"],
                public_key=config["public_key"],
                private_key=config["private_key"]
            )

            plans = braintree_manager.get_all_plans()

            if plans:
                for plan in plans:
                    customer_id, payment_method_token = braintree_manager.create_customer(customer_data)
                    if customer_id and payment_method_token:
                        success = braintree_manager.subscribe_customer_to_plan(payment_method_token, plan.id)
                        if success:
                            print(f"Customer {customer_id} subscribed to plan {plan.id} successfully.")
                        else:
                            print(f"Failed to subscribe customer {customer_id} to plan {plan.id}.")
            else:
                print("No plans available to subscribe.")
    else:
        print("Gateway configuration or customer data not found or invalid.")