import pytest
from conftest import refresh_gui
from gi.repository import Gtk
from wiring import SingletonScope
from wiring.scanning import scan_to_graph

from tomate_gtk.dialogs.preference import (ExtensionStack, PreferenceDialog,
                                           TimerDurationStack)


@pytest.fixture
def extension_mock(mocker):
    return mocker.Mock(widget=Gtk.Button())


@pytest.fixture
def preference(extension_mock, mocker):
    return PreferenceDialog(mocker.Mock(widget=Gtk.Button()), extension_mock)


def test_preference_extension_module(graph, config, plugin_manager, lazy_proxy):
    scan_to_graph(['tomate_gtk.dialogs.preference'], graph)

    assert 'view.preference.extension' in graph.providers

    provider = graph.providers['view.preference.extension']

    assert provider.scope == SingletonScope
    assert isinstance(graph.get('view.preference.extension'), ExtensionStack)


def test_preference_duration_module(graph, config):
    scan_to_graph(['tomate_gtk.dialogs.preference'], graph)

    assert 'view.preference.duration' in graph.providers

    provider = graph.providers['view.preference.duration']

    assert provider.scope == SingletonScope
    assert isinstance(graph.get('view.preference.duration'), TimerDurationStack)


def test_preference_module(graph, config, mocker):
    scan_to_graph(['tomate_gtk.dialogs.preference'], graph)

    assert 'view.preference' in graph.providers

    provider = graph.providers['view.preference']

    assert provider.scope == SingletonScope

    graph.register_instance('tomate.config', config)
    graph.register_factory('tomate.plugin', mocker.Mock)
    graph.register_factory('tomate.proxy', mocker.Mock)
    graph.register_factory('view.preference.extension', ExtensionStack)
    graph.register_factory('view.preference.duration', TimerDurationStack)

    assert isinstance(graph.get('view.preference'), PreferenceDialog)


@pytest.fixture
def plugin(mocker):
    plug = mocker.Mock(version='1.1.1', description='description')
    plug.name = 'plugin'
    return plug


def test_deactive_plugin_settings_button_when_plugin_when_has_not_settings(plugin_manager, config, lazy_proxy, plugin):
    plugin.plugin_object.is_activated = True
    plugin.plugin_object.is_activated = False
    setup_plugin_manager(plugin_manager, plugin)

    extension_stack = ExtensionStack(plugin_manager, config, lazy_proxy)
    extension_stack.refresh()
    refresh_gui(0)

    assert extension_stack.plugin_settings_button.get_sensitive() is False


def test_activate_plugin_settings_button_when_plugin_has_settings(plugin_manager, config, lazy_proxy, plugin):
    plugin.plugin_object.is_activated = True
    plugin.plugin_object.has_settings = True
    setup_plugin_manager(plugin_manager, plugin)

    extension_stack = ExtensionStack(plugin_manager, config, lazy_proxy)
    extension_stack.refresh()
    refresh_gui(0)

    assert extension_stack.plugin_settings_button.get_sensitive() is True


def test_show_plugin_settings(plugin_manager, config, lazy_proxy, plugin, mocker):
    plugin.plugin_object.is_activated = True
    plugin.has_settings = True
    setup_plugin_manager(plugin_manager, plugin)
    view = mocker.Mock(widget='widget')
    lazy_proxy.side_effect = lambda name: view if name == 'view.preference' else None

    extension_stack = ExtensionStack(plugin_manager, config, lazy_proxy)
    extension_stack.refresh()
    extension_stack.plugin_settings_button.emit('clicked')
    refresh_gui(0)

    plugin.plugin_object.settings_window.return_value.set_transient_for('widget')
    plugin.plugin_object.settings_window.return_value.run.assert_called_once_with()


def setup_plugin_manager(plugin_manager, plugin):
    plugin_manager.getAllPlugins.return_value = [plugin, ]
    plugin_manager.getPluginByName.side_effect = lambda name: plugin if name == plugin.name else None


def test_preference_widget(preference):
    assert preference.widget is preference


def test_refresh_plugins(preference, extension_mock):
    preference.refresh_plugins()

    extension_mock.refresh.assert_called_once_with()
