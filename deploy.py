import argparse
import subprocess
from collections import OrderedDict

import yaml


def ordered_load(stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


def ordered_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def cmd_runner(command, caller):
    result = subprocess.run(command, shell=True, capture_output=True)
    if result.stderr:
        print("Error:", result.stderr)
    if result.stdout:
        print("Helm => ", caller, " Out => ", result.stdout.decode('utf-8'), "\n")


class LanguageConfig:

    def __init__(self, language_code, base_name, helm_chart_path):
        self.language_code = language_code
        self.helm_chart_path = helm_chart_path
        self.release_name = "{}-{}".format(base_name, language_code)
        print("Release name", self.release_name)

    def is_deployed(self, namespace):
        result = subprocess.getoutput('helm status {} -n {} --output yaml'.format(self.release_name, namespace))
        if "release: not found" in result.lower():
            return False
        else:
            return True

    def get_language_code(self):
        return self.language_code

    def get_language_code_as_list(self):
        return [self.language_code]

    def deploy(self, namespace, api_changed, gpu_count, enable_gpu, cpu_count, image_name,
               image_version):
        is_deployed = self.is_deployed(namespace)
        print("IS_DEPLOYED", is_deployed)
        if is_deployed == True:
            process = "upgrade"
            if api_changed == True:
                uninstall_command = "helm uninstall {0} --namespace {1}".format(self.release_name.replace('_', '-'),
                                                                                namespace)
                cmd_runner(uninstall_command, "LANGUAGE :" + self.language_code)
                process = "install"
        else:
            process = "install"

        pull_policy = "Always" if api_changed == True else "IfNotPresent"

        set_gpu_command = "--set resources.limits.\"nvidia\.com/gpu\"='{}' --set env.gpu='{}'".format(
            gpu_count, enable_gpu)
        set_cpu_command = "--set resources.requests.cpu='{}' --set env.gpu='{}'".format(cpu_count, False)

        command = "helm {0} --timeout 180s {1} {2} --namespace {3} --set env.languages='[\"{4}\"]' --set image.pullPolicy='{5}' --set image.repository='{6}' --set image.tag='{7}'".format(
            process, self.release_name.replace('_', '-'), self.helm_chart_path, namespace, self.language_code,
            pull_policy, image_name,
            image_version)
        if enable_gpu == True:
            command = "{} {}".format(command, set_gpu_command)
        else:
            command = "{} {}".format(command, set_cpu_command)
        print(command)
        cmd_runner(command, "LANGUAGE :" + self.language_code)


class MultiLanguageConfig:

    def __init__(self, language_code_list, base_name, helm_chart_path):
        self.language_code_list = language_code_list.replace('_', '-')
        self.helm_chart_path = helm_chart_path
        self.languages_codes_string = "-".join(language_code_list)
        self.release_name = "{}-{}".format(base_name, self.languages_codes_string)
        print("Release name", self.release_name)

    def is_deployed(self, namespace):
        result = subprocess.getoutput('helm status {} -n {} --output yaml'.format(self.release_name.replace('_', '-'), namespace))
        if "release: not found" in result.lower():
            return False
        else:
            return True

    def get_language_code(self):
        return self.languages_codes_string

    def get_language_code_as_list(self):
        return self.language_code_list

    def deploy(self, namespace, api_changed, gpu_count, enable_gpu, cpu_count, image_name,
               image_version):
        if len(self.language_code_list) == 0:
            raise ValueError("No Language codes present.Please add language codes or remove the item from list")
            return
        is_deployed = self.is_deployed(namespace)
        print("IS_DEPLOYED", is_deployed)
        if is_deployed == True:
            process = "upgrade"
            if api_changed == True:
                uninstall_command = "helm uninstall {0} --namespace {1}".format(self.release_name.replace('_', '-'), namespace)
                cmd_runner(uninstall_command, "LANGUAGE :" + ",".join(self.language_code_list))
                process = "install"
        else:
            process = "install"

        pull_policy = "Always" if api_changed == True else "IfNotPresent"

        set_gpu_command = "--set resources.limits.\"nvidia\.com/gpu\"='{}' --set env.gpu='{}'".format(
            gpu_count, enable_gpu)
        set_cpu_command = "--set resources.requests.cpu='{}' --set env.gpu='{}'".format(cpu_count, False)

        languages = ["\"{}\"".format(x) for x in self.language_code_list]
        languages = "\,".join(languages)
        command = "helm {0} --timeout 180s {1} {2} --namespace {3} --set env.languages='[{4}]' --set image.pullPolicy='{5}' --set image.repository='{6}' --set image.tag='{7}'".format(
            process, self.release_name.replace('_', '-'), self.helm_chart_path, namespace, languages, pull_policy, image_name,
            image_version)
        if enable_gpu == True:
            command = "{} {}".format(command, set_gpu_command)
        else:
            command = "{} {}".format(command, set_cpu_command)
        print(command)
        cmd_runner(command, "LANGUAGE :" + ",".join(self.language_code_list))


class EnvoyConfig:

    def __init__(self, base_name, helm_chart_path):
        self.name = "envoy"
        self.helm_chart_path = helm_chart_path
        self.release_name = "{}-{}".format(base_name, self.name)

    def is_deployed(self, namespace):
        result = subprocess.getoutput('helm status {} -n {} --output yaml'.format(self.release_name.replace('_', '-'), namespace))
        if "release: not found" in result.lower():
            return False
        else:
            return True

    def deploy(self, namespace, enable_ingress):
        isdeployed = self.is_deployed(namespace)
        if not isdeployed:
            process = "install"
        else:
            process = "upgrade"

        command = "helm {0} --timeout 180s {1} {2} --namespace {3} --set ingress.enabled='{4}'".format(process,
                                                                                                       self.release_name.replace('_', '-'),
                                                                                                       self.helm_chart_path,
                                                                                                       namespace,
                                                                                                       enable_ingress)
        cmd_runner(command, "Envoy")


class ProxyConfig:

    def __init__(self, base_name, helm_chart_path):
        self.name = "proxy"
        self.helm_chart_path = helm_chart_path
        self.release_name = "{}-{}".format(base_name, self.name)

    def is_deployed(self, namespace):
        result = subprocess.getoutput('helm status {} -n {} --output yaml'.format(self.release_name.replace('_', '-'), namespace))
        if "release: not found" in result.lower():
            return False
        else:
            return True

    def deploy(self, namespace):
        isdeployed = self.is_deployed(namespace)
        if not isdeployed:
            process = "install"
        else:
            process = "upgrade"

        command = "helm {0} --timeout 180s {1} {2} --namespace {3} ".format(process,
                                                                            self.release_name.replace('_', '-'),
                                                                            self.helm_chart_path,
                                                                            namespace
                                                                            )
        cmd_runner(command, "proxy")


def read_app_config(config_path):
    with open(config_path, "r") as stream:
        try:
            config = ordered_load(stream, yaml.SafeLoader)
            return config
        except yaml.YAMLError as exc:
            print("Error: ", exc)
            return None


def read_envoy_config(config_path):
    with open(config_path, "r") as stream:
        try:
            config = ordered_load(stream, yaml.SafeLoader)
            return config
        except yaml.YAMLError as exc:
            print("Error: ", exc)
            return None


def get_cluster(clusters, language_code):
    cluster_name = "{}_cluster".format(language_code)
    for cluster in clusters:
        if cluster["name"] == cluster_name:
            return cluster
    return None


def clear_clusters_and_matches(config, removed_releases):
    if len(removed_releases) == 0:
        print("No unused clusters in envoy to clear")
        return
    listeners = config["static_resources"]["listeners"]
    clusters = config["static_resources"]["clusters"]
    routes = listeners[0]["filter_chains"][0]["filters"][0]["typed_config"]["route_config"]["virtual_hosts"][0][
        "routes"]

    for cluster in clusters:
        address = \
        cluster["load_assignment"]["endpoints"][0]["lb_endpoints"][0]["endpoint"]["address"]["socket_address"][
            "address"]
        if address.rstrip().lstrip() in removed_releases:
            clusters.remove(cluster)
        cluster_name = cluster["name"]
        for route in routes:
            if "route" in route:
                if route["route"]["cluster"] == cluster_name:
                    routes.remove(route)


def create_cluster(language_code, release_name):
    cluster = '''
        name: hi_cluster
        type: LOGICAL_DNS
        lb_policy: ROUND_ROBIN
        connect_timeout: 30s
        dns_lookup_family: V4_ONLY
        typed_extension_protocol_options:
          envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
            "@type": type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions
            explicit_http_config:
              http2_protocol_options: {}
        load_assignment:
          cluster_name: hi_cluster
          endpoints:
          - lb_endpoints:
            - endpoint:
                address:
                  socket_address:
                    address: asr-model-v2-hi
                    port_value: 50051
    '''
    cluster = ordered_load(cluster, yaml.SafeLoader)
    cluster_name = "{}_cluster".format(language_code)
    cluster["name"] = cluster_name
    cluster["load_assignment"]["cluster_name"] = cluster_name
    cluster["load_assignment"]["endpoints"][0]["lb_endpoints"][0]["endpoint"]["address"]["socket_address"][
        "address"] = release_name
    return cluster


def verify_and_update_release_name(cluster, release_name):
    address = cluster["load_assignment"]["endpoints"][0]["lb_endpoints"][0]["endpoint"]["address"]["socket_address"][
        "address"]
    if address != release_name:
        cluster["load_assignment"]["endpoints"][0]["lb_endpoints"][0]["endpoint"]["address"]["socket_address"][
            "address"] = release_name


def update_envoy_config(config, language_config):
    methods_config = [
        {"name": "recognize", "enable_grpc_match": True, "enable_rest_match": True},
        {"name": "punctuate", "enable_grpc_match": True, "enable_rest_match": True},
        {"name": "recognize_audio", "enable_grpc_match": True, "enable_rest_match": False}
    ]

    listeners = config["static_resources"]["listeners"]
    clusters = config["static_resources"]["clusters"]
    routes = listeners[0]["filter_chains"][0]["filters"][0]["typed_config"]["route_config"]["virtual_hosts"][0][
        "routes"]

    # updating cluster information
    cluster = get_cluster(clusters, language_config.get_language_code())
    if cluster is None:
        lang_cluster = create_cluster(language_config.get_language_code(), language_config.release_name)
        clusters.append(lang_cluster)
        cluster = lang_cluster
    else:
        verify_and_update_release_name(cluster, language_config.release_name)
    # updating match filter
    language_codes = language_config.get_language_code_as_list()
    initial_routes_length = len(routes)
    for language_code in language_codes:
        for method_config in methods_config:
            method_name = method_config["name"]
            if "enable_grpc_match" in method_config and (method_config["enable_grpc_match"] == True):
                grpc_match_route = get_grpc_match_filter(method_name, routes, language_code)
                if grpc_match_route is None:
                    grpc_match_route = create_grpc_match_filter(method_name, language_code, cluster["name"])
                    routes.insert(len(routes) - initial_routes_length, grpc_match_route)

            if "enable_rest_match" in method_config and (method_config["enable_rest_match"] == True):
                rest_match_route = get_rest_match_filter(method_name, routes, language_code)
                if rest_match_route is None:
                    rest_match_route = create_rest_match_filter(method_name, language_code, cluster["name"])
                    routes.insert(len(routes) - initial_routes_length, rest_match_route)

    return config


def write_to_yaml(config, path):
    with open(path, "w") as file:
        try:
            ordered_dump(config, stream=file, Dumper=yaml.SafeDumper)
        except yaml.YAMLError as exc:
            print("Error: ", exc)


def create_grpc_match_filter(method_name, language_code, cluster_name):
    route_match = '''
        match:
          path: "/ekstep.speech_recognition.SpeechRecognizer/{}"
          headers:
          - name: language
            exact_match: "hi"
        route:
          cluster: hi_cluster
          timeout: 60s
    '''.format(method_name)
    route_match = ordered_load(route_match, yaml.SafeLoader)
    route_match["match"]["headers"][0]["exact_match"] = language_code
    route_match["route"]["cluster"] = cluster_name
    return route_match


def create_rest_match_filter(method_name, language_code, cluster_name):
    route_match = '''
        match:
          path: "/v1/{}/hi"
          headers:
          - name: Content-Type
            exact_match: application/json
        route:
          cluster: hi_cluster
          timeout: 60s
    '''.format(method_name)
    route_match = ordered_load(route_match, yaml.SafeLoader)
    route_match["match"]["path"] = "/v1/{}/{}".format(method_name, language_code)
    route_match["route"]["cluster"] = cluster_name
    return route_match


def get_grpc_match_filter(method_name, routes, language_code):
    path_to_match = "/ekstep.speech_recognition.SpeechRecognizer/{}".format(method_name)
    for route in routes:
        if "path" in route["match"] and route["match"]["path"] == path_to_match:
            if "headers" in route["match"] and route["match"]["headers"][0]["exact_match"] == language_code:
                return route
    return None


def get_rest_match_filter(method_name, routes, language_code):
    path_to_match = "/v1/{}/{}".format(method_name, language_code)
    for route in routes:
        if "path" in route["match"] and route["match"]["path"] == path_to_match:
            return route
    return None


def update_proto_descriptor(config, path_to_pb_file):
    pass


def get_releases(base_name, namespace):
    result = subprocess.getoutput('helm list -f "^{}-(.*)" -n {} -o yaml'.format(base_name, namespace))
    release_list = ordered_load(result, yaml.SafeLoader)
    return [release["name"] for release in release_list if
            release["name"] != "{}-envoy".format(base_name) and release["name"] != "{}-proxy".format(base_name)]


def uninstall_release(release, namespace):
    command = "helm uninstall {} -n {}".format(release, namespace)
    cmd_runner(command, "Remove: {}".format(release))


def remove_unwanted_releases(new_releases, existing_releases, namespace):
    removed_releases = []
    for release in existing_releases:
        if release not in new_releases:
            uninstall_release(release, namespace)
            removed_releases.append(release)
    return removed_releases


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--namespace', default='test-v2', help="Namespace to use")
    # parser.add_argument('--app-config-path', help="Path of the app config")
    parser.add_argument('--enable-ingress', help="enable ingress to be deployed", default='false')
    parser.add_argument('--image-name', help="Model api image name", required=True)
    parser.add_argument('--image-version', help="Model api image version", required=True)
    parser.add_argument('--api-updated', default='false', help="Flag if api has changed")

    args = parser.parse_args()

    enable_ingress = args.enable_ingress
    image_name = args.image_name
    image_version = args.image_version
    namespace = args.namespace
    api_updated = args.api_updated
    app_config_path = "app_config.yaml"
    envoy_config_path = "infra/envoy/config.yaml"
    language_helm_chart_path = "infra/asr-model-v2"
    envoy_helm_chart_path = "infra/envoy"
    proxy_helm_chart_path = "infra/asr-proxy"
    envoy_config = read_envoy_config(envoy_config_path)
    app_config = read_app_config(app_config_path)

    # Argparse library parses all parameters as string. Make sure to handle the boolean values

    if api_updated == 'true':
        api_updated = True
    else:
        api_updated = False

    if enable_ingress == 'true':
        enable_ingress = True
    else:
        enable_ingress = False

    if envoy_config is None:
        print("Check the envoy config file")
        exit()
    if app_config is None:
        print("Check the app config file")
        exit()

    release_base_name = app_config["base_name"]
    configuration = app_config["config"]

    existing_releases = get_releases(release_base_name, namespace)
    new_releases = []
    for item in configuration:
        gpu_count = 0
        cpu_count = 0
        enable_gpu = False
        languages = []
        if "languages" in item:
            languages = item["languages"]
        if "gpu" in item:
            gpu_count = item["gpu"]["count"]
            enable_gpu = True
        if "cpu" in item:
            cpu_count = item["cpu"]["count"]

        if len(languages) == 0:
            continue
        elif len(languages) == 1:
            language_code = languages[0]
            language_config = LanguageConfig(language_code, release_base_name, language_helm_chart_path)
            language_config.deploy(namespace, api_updated, gpu_count, enable_gpu, cpu_count,
                                   image_name, image_version)
            envoy_config = update_envoy_config(envoy_config, language_config)
            new_releases.append(language_config.release_name)
        else:
            language_config = MultiLanguageConfig(languages, release_base_name, language_helm_chart_path)
            language_config.deploy(namespace, api_updated, gpu_count, enable_gpu, cpu_count,
                                   image_name, image_version)
            envoy_config = update_envoy_config(envoy_config, language_config)
            new_releases.append(language_config.release_name)

    remove_unwanted_releases(new_releases, existing_releases, namespace)

    write_to_yaml(envoy_config, envoy_config_path)
    EnvoyConfig(release_base_name, envoy_helm_chart_path).deploy(namespace, enable_ingress)
    ProxyConfig(release_base_name, proxy_helm_chart_path).deploy(namespace)
