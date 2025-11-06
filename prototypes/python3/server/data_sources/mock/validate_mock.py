import json
import jsonschema
import mock
from referencing import Registry, Resource
from pathlib import Path

def load_schema(file):
    try:
        with open(file, 'r') as json_file:
            machine_schema = json.load(json_file)
            return machine_schema
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}")
        return None
    
def create_schema_registry(types):
    # load schemas
    # create a registry with all the schemas  
    registry = Registry()
    for type in types:
        schema = load_schema(type["schema"])
        registry = registry.with_resource(f"{type["namespaceUri"]}/{type["elementId"]}/v1.0", Resource.from_contents(schema))
    return registry

def create_validator(instance, registry):
    main_schema = registry.contents(f"{instance["namespaceUri"]}/{instance["typeId"]}/v1.0")
    validator_cls = jsonschema.validators.validator_for(main_schema)
    return validator_cls(main_schema, registry=registry)

def validate_instances(debug=False):
    invalid_instances = 0

    #load mock data
    types = mock.I3X_DATA["objectTypes"]
    instances = mock.I3X_DATA["instances"]

    registry = create_schema_registry(types)

    # create a validator for the instance's type
    for instance in instances:
        if debug:
            print(f"checking instance: ", instance["elementId"], " of type", instance["typeId"])
        if "values" in instance:
            validator = create_validator(instance, registry)

            # validate the data
            instance_data = instance["values"]
            for value in instance_data:
                try:
                    validator.validate(value)
                    if debug:
                        print(f"\tValidated passed")
                except jsonschema.exceptions.ValidationError as ve:
                    if debug:
                        print(f"\tValidation error: {ve.message}")
                    invalid_instances += 1
        else:
            if debug:
                print(f"\tSkip. No values to validate for this instance.")
    return invalid_instances

if __name__ == "__main__":
    num_invalid_instances = validate_instances()
    print(num_invalid_instances)