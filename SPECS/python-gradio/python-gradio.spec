# SPDX-FileCopyrightText: (C) 2026 Institute of Software, Chinese Academy of Sciences (ISCAS)
# SPDX-FileCopyrightText: (C) 2026 openRuyi Project Contributors
# SPDX-FileContributor: Li Guan <guanli.oerv@isrc.iscas.ac.cn>
#
# SPDX-License-Identifier: MulanPSL-2.0

%global srcname gradio

Name:           python-%{srcname}
Version:        6.31.0
Release:        %autorelease
Summary:        Python library for easily interacting with trained machine learning models
License:        Apache-2.0
URL:            https://github.com/gradio-app/gradio
#!RemoteAsset:  sha256:40cf094fe8ea1b8ada0fc4c10b685c4c5f09c4061d34c073be25bab342e14e22
Source0:        https://files.pythonhosted.org/packages/source/g/%{srcname}/%{srcname}-%{version}.tar.gz
BuildArch:      noarch
BuildSystem:    pyproject

BuildOption(install):  -l %{srcname}
# Triggers FileNotFoundError by scanning a local 'themes' directory during module import.
BuildOption(check):  -e gradio.themes.app
# Triggers network error by downloading a remote AWS S3 image during module import.
BuildOption(check):  -e gradio.themes.builder_app

BuildRequires:  pyproject-rpm-macros
BuildRequires:  pkgconfig(python3)
# For tests
BuildRequires:  python3dist(urllib3)

Provides:       python3-%{srcname} = %{version}-%{release}
%python_provide python3-%{srcname}

%description
Build and share delightful machine learning apps, all in Python.

%prep -a
sed -i 's/tomlkit>=0.12.0,<0.15.0/tomlkit>=0.12.0/g' requirements.txt
sed -i 's/Requires-Dist: tomlkit<0.15.0,>=0.12.0/Requires-Dist: tomlkit>=0.12.0/g' PKG-INFO

# Backport Pillow 13 compatibility from https://github.com/gradio-app/gradio/pull/14005
sed -i 's/pillow>=8.0,<13.0/pillow>=8.0,<14.0/' requirements.txt
sed -i '/^Requires-Dist: pillow/s/<13\.0/<14.0/' PKG-INFO

%generate_buildrequires
%pyproject_buildrequires

%files -f %{pyproject_files}
%doc README.md
%license LICENSE
%{_bindir}/gradio
%{_bindir}/upload_theme
%{python3_sitelib}/gradio/_simple_templates/simpledropdown.pyi
%{python3_sitelib}/gradio/_simple_templates/simpleimage.pyi
%{python3_sitelib}/gradio/_simple_templates/simpletextbox.pyi
%{python3_sitelib}/gradio/blocks_events.pyi
%{python3_sitelib}/gradio/components/annotated_image.pyi
%{python3_sitelib}/gradio/components/api_component.pyi
%{python3_sitelib}/gradio/components/audio.pyi
%{python3_sitelib}/gradio/components/base.pyi
%{python3_sitelib}/gradio/components/browser_state.pyi
%{python3_sitelib}/gradio/components/button.pyi
%{python3_sitelib}/gradio/components/chatbot.pyi
%{python3_sitelib}/gradio/components/checkbox.pyi
%{python3_sitelib}/gradio/components/checkboxgroup.pyi
%{python3_sitelib}/gradio/components/clear_button.pyi
%{python3_sitelib}/gradio/components/code.pyi
%{python3_sitelib}/gradio/components/color_picker.pyi
%{python3_sitelib}/gradio/components/custom_html_components/audio_gallery.pyi
%{python3_sitelib}/gradio/components/custom_html_components/colored_checkbox_group.pyi
%{python3_sitelib}/gradio/components/dataframe.pyi
%{python3_sitelib}/gradio/components/dataset.pyi
%{python3_sitelib}/gradio/components/datetime.pyi
%{python3_sitelib}/gradio/components/deep_link_button.pyi
%{python3_sitelib}/gradio/components/dialogue.pyi
%{python3_sitelib}/gradio/components/download_button.pyi
%{python3_sitelib}/gradio/components/dropdown.pyi
%{python3_sitelib}/gradio/components/duplicate_button.pyi
%{python3_sitelib}/gradio/components/fallback.pyi
%{python3_sitelib}/gradio/components/file.pyi
%{python3_sitelib}/gradio/components/file_explorer.pyi
%{python3_sitelib}/gradio/components/gallery.pyi
%{python3_sitelib}/gradio/components/highlighted_text.pyi
%{python3_sitelib}/gradio/components/html.pyi
%{python3_sitelib}/gradio/components/image.pyi
%{python3_sitelib}/gradio/components/image_editor.pyi
%{python3_sitelib}/gradio/components/imageslider.pyi
%{python3_sitelib}/gradio/components/json_component.pyi
%{python3_sitelib}/gradio/components/label.pyi
%{python3_sitelib}/gradio/components/login_button.pyi
%{python3_sitelib}/gradio/components/markdown.pyi
%{python3_sitelib}/gradio/components/model3d.pyi
%{python3_sitelib}/gradio/components/multimodal_textbox.pyi
%{python3_sitelib}/gradio/components/native_plot.pyi
%{python3_sitelib}/gradio/components/navbar.pyi
%{python3_sitelib}/gradio/components/number.pyi
%{python3_sitelib}/gradio/components/paramviewer.pyi
%{python3_sitelib}/gradio/components/plot.pyi
%{python3_sitelib}/gradio/components/radio.pyi
%{python3_sitelib}/gradio/components/slider.pyi
%{python3_sitelib}/gradio/components/state.pyi
%{python3_sitelib}/gradio/components/textbox.pyi
%{python3_sitelib}/gradio/components/timer.pyi
%{python3_sitelib}/gradio/components/upload_button.pyi
%{python3_sitelib}/gradio/components/video.pyi
%{python3_sitelib}/gradio/components/workflowcanvas.pyi
%{python3_sitelib}/gradio/hash_seed.txt
%{python3_sitelib}/gradio/layouts/accordion.pyi
%{python3_sitelib}/gradio/layouts/column.pyi
%{python3_sitelib}/gradio/layouts/draggable.pyi
%{python3_sitelib}/gradio/layouts/form.pyi
%{python3_sitelib}/gradio/layouts/group.pyi
%{python3_sitelib}/gradio/layouts/row.pyi
%{python3_sitelib}/gradio/layouts/sidebar.pyi
%{python3_sitelib}/gradio/layouts/tabs.pyi
%{python3_sitelib}/gradio/layouts/walkthrough.pyi
%{python3_sitelib}/gradio/templates.pyi

%changelog
%autochangelog
