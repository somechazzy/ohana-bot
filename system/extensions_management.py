import importlib.util
import inspect
import pathlib
import sys
import traceback

from extensions.templates.events import _BaseEventHandler  # noqa

from utils.helpers.context_helpers import create_isolated_task

extensions: dict[str, dict[str, list[type]]] = {
    # event_group: {event_name: [list of extension classes]}
}


def load_extensions(clear_existing: bool = False):
    from common.app_logger import AppLogger
    logger = AppLogger("extensions_management")
    base_path = pathlib.Path(r"extensions").resolve()
    if clear_existing:
        extensions.clear()
    loaded_extensions_count = 0
    for path in base_path.rglob("*.py"):
        if not path.is_file() or base_path.joinpath("templates") in path.parents:
            continue
        module_name = path.relative_to(base_path).with_suffix("").as_posix().replace("/", ".")
        full_module_name = f"{base_path}.{module_name}"

        try:
            spec = importlib.util.spec_from_file_location(full_module_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[full_module_name] = module
            spec.loader.exec_module(module)
            loaded_extensions_count += 1
            for _, cls in inspect.getmembers(module, inspect.isclass):
                if cls.__module__ != module.__name__:
                    continue
                try:
                    if issubclass(cls, _BaseEventHandler):
                        if cls.event_group() not in extensions:
                            extensions[cls.event_group()] = {}
                        if cls.event_name() not in extensions[cls.event_group()]:
                            extensions[cls.event_group()][cls.event_name()] = []
                        extensions[cls.event_group()][cls.event_name()].append(cls)
                    else:
                        loaded_extensions_count -= 1
                except Exception as e:
                    logger.warning(f"Error loading extension {cls.__name__} from {module_name}: {e}",
                                   extras={"traceback": traceback.format_exc()})
                    loaded_extensions_count -= 1
        except Exception as e:
            logger.warning(f"Error loading module {module_name}: {e}",
                           extras={"traceback": traceback.format_exc()})

    logger.info(f"Loaded {loaded_extensions_count} extensions.")


async def propagate_to_extensions(*args, event_group: str, event: str):
    """
    Executes the appropriate extension handlers based on the event type.
    """
    from common.app_logger import AppLogger
    logger = AppLogger("extensions_management")
    event_extensions = extensions.get(event_group, {}).get(event, [])
    if not event_extensions:
        return
    logger.debug(f"Propagating event {event_group}.{event} to {len(event_extensions)} extensions")
    for extension_class in event_extensions:
        try:
            extension_handler = extension_class(*args)
            if await extension_handler.check():
                create_isolated_task(extension_handler.handle_event())
        except Exception as e:
            logger.error(f"Error in extension {extension_class.__name__} for event {event_group}.{event}: {e}")
