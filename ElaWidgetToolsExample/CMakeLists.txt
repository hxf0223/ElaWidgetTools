cmake_minimum_required(VERSION 3.5)
cmake_policy(SET CMP0087 NEW)
project(ElaWidgetToolsExample VERSION 0.1 LANGUAGES CXX)

FILE(GLOB ORIGIN *.cpp *.h)
FILE(GLOB MODELVIEW ModelView/*.h ModelView/*.cpp)
FILE(GLOB EAXMPLEPAGE ExamplePage/*.h ExamplePage/*.cpp)

source_group(ModelView FILES ${MODELVIEW})
source_group(ExamplePage FILES ${EAXMPLEPAGE})

set(PROJECT_SOURCES
    ${ORIGIN}
    ${MODELVIEW}
    ${EAXMPLEPAGE}
)

if(${QT_VERSION_MAJOR} GREATER_EQUAL 6)
    qt_add_executable(${PROJECT_NAME}
        MANUAL_FINALIZATION
        ${PROJECT_SOURCES}
    )

    # 遍历所有资源文件
    file(GLOB_RECURSE RES_PATHS *.png *.jpg *.svg *.ico *.ttf *.webp *.js)

    foreach(filepath ${RES_PATHS})
        string(REPLACE "${CMAKE_CURRENT_SOURCE_DIR}/" "" filename ${filepath})
        list(APPEND resource_files ${filename})
    endforeach(filepath)

    qt_add_resources(${PROJECT_NAME} "ElaWidgetToolsExample"
        RESOURCES PREFIX "/"
        FILES
        ${resource_files}
    )
else()
    qt5_add_big_resources(PROJECT_SOURCES
        ElaWidgetToolsExample.qrc
    )
    add_executable(${PROJECT_NAME}
        ${PROJECT_SOURCES}
    )
endif()

if(WIN32)
    target_include_directories(${PROJECT_NAME} PUBLIC
        ExamplePage
        ModelView
    )

    if(BUILD_ELAPACKETIO)
        target_link_libraries(${PROJECT_NAME} PRIVATE
            Qt${QT_VERSION_MAJOR}::Widgets
            ElaWidgetTools
            ElaPacketIO
        )
    else()
        target_link_libraries(${PROJECT_NAME} PRIVATE
            Qt${QT_VERSION_MAJOR}::Widgets
            ElaWidgetTools
        )
    endif()

else()
    target_include_directories(${PROJECT_NAME} PUBLIC
        ExamplePage
        ModelView
    )
    target_link_libraries(${PROJECT_NAME} PRIVATE
        Qt${QT_VERSION_MAJOR}::Widgets
        ElaWidgetTools
    )
endif()

if(${QT_VERSION} VERSION_LESS 6.1.0)
    set(BUNDLE_ID_OPTION MACOSX_BUNDLE_GUI_IDENTIFIER com.example.${PROJECT_NAME})
endif()

set_target_properties(${PROJECT_NAME} PROPERTIES
    ${BUNDLE_ID_OPTION}
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
    VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_INSTALL_PREFIX}/${PROJECT_NAME}"
    VS_DEBUGGER_COMMAND "${CMAKE_INSTALL_PREFIX}/${PROJECT_NAME}/${PROJECT_NAME}.exe"
)

if(QT_VERSION_MAJOR EQUAL 6)
    qt_finalize_executable(${PROJECT_NAME})
endif()

if(WIN32 AND NOT UNIX)
    get_target_property(qmake_executable Qt6::qmake IMPORTED_LOCATION)
    get_filename_component(_qt_bin_dir "${qmake_executable}" DIRECTORY)
    find_program(WINDEPLOYQT_EXECUTABLE windeployqt HINTS "${_qt_bin_dir}")
    message(STATUS "Using windeployqt: ${WINDEPLOYQT_EXECUTABLE}")
    message(STATUS "qt bin dir: ${_qt_bin_dir}")

    # 部署Qt运行时和QML依赖
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
        COMMAND "${WINDEPLOYQT_EXECUTABLE}"
        $<$<CONFIG:Debug>:--debug>
        $<$<NOT:$<CONFIG:Debug>>:--release>
        --libdir $<TARGET_FILE_DIR:${PROJECT_NAME}>
        --verbose 0
        --compiler-runtime
        --no-opengl-sw
        --force
        --plugindir "$<TARGET_FILE_DIR:${PROJECT_NAME}>/plugins"
        $<TARGET_FILE:${PROJECT_NAME}>
        COMMENT "Deploying Qt with QML dependencies..."
    )

    # Also run windeployqt on dependent library targets so their Qt imports are detected
    # and included in the application's runtime dir. Add any library targets here that
    # are built as part of the same project and may have Qt runtime dependencies.
    set(WINDEPLOYQT_DEPENDENT_TARGETS
        gcMAVComm
        gcMAVInspector
    )

    foreach(_dep ${WINDEPLOYQT_DEPENDENT_TARGETS})
        if(TARGET ${_dep})
            add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
                COMMAND "${WINDEPLOYQT_EXECUTABLE}"
                $<$<CONFIG:Debug>:--debug>
                $<$<NOT:$<CONFIG:Debug>>:--release>
                --libdir $<TARGET_FILE_DIR:${PROJECT_NAME}>
                --verbose 0
                --compiler-runtime
                --no-opengl-sw
                --force
                --qml
                ${QML_DIR_ARGS}
                --plugindir "$<TARGET_FILE_DIR:${PROJECT_NAME}>/plugins"
                $<TARGET_FILE:${_dep}>
                COMMENT "Deploying Qt dependencies for ${_dep}..."
            )
        endif()
    endforeach()

    if(QT_VERSION_MAJOR EQUAL 6)
        qt_finalize_executable(${PROJECT_NAME})
    endif()

    include(GNUInstallDirs)
    install(PROGRAMS
        $<TARGET_FILE:${PROJECT_NAME}>
        DESTINATION . # TYPE BIN
    )

    # 安装所有DLL文件
    install(DIRECTORY
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/
        DESTINATION .
        FILES_MATCHING PATTERN "*.dll"
    )

    # 安装Qt插件
    install(DIRECTORY
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/plugins/
        DESTINATION plugins
        OPTIONAL
    )

    # 安装Qt QML模块 (windeployqt自动检测到的Qt QML运行时模块)
    install(DIRECTORY
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/qml/
        DESTINATION qml
        OPTIONAL
        PATTERN "mapMonitor" EXCLUDE
        PATTERN "NuoQianMap" EXCLUDE
    )

    # 安装翻译文件
    install(DIRECTORY
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/translations/
        DESTINATION translations
        OPTIONAL
    )

    # 安装其他资源文件 (如果有)
    install(FILES
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/nuoqian_map.ini
        DESTINATION .
        OPTIONAL
    )

    # 安装NuoQianMap相关文件
    install(DIRECTORY
        $<TARGET_FILE_DIR:${PROJECT_NAME}>/nuoqian_maps/
        DESTINATION nuoqian_maps
        OPTIONAL
    )

    include(CPACK REQUIRED) # include(CPackIFW REQUIRED)
endif()
