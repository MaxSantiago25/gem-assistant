use tauri::{AppHandle, Manager, PhysicalPosition, PhysicalSize, Position, Size};

#[tauri::command]
fn set_island_expanded(app: AppHandle, expanded: bool) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("island") {
        let monitor_opt = window
            .current_monitor()
            .ok()
            .flatten()
            .or_else(|| window.primary_monitor().ok().flatten());

        if let Some(monitor) = monitor_opt {
            let monitor_size = monitor.size();
            let scale_factor = monitor.scale_factor();

            let (target_width, target_height) = if expanded {
                ((960.0 * scale_factor) as u32, (620.0 * scale_factor) as u32)
            } else {
                ((360.0 * scale_factor) as u32, (80.0 * scale_factor) as u32)
            };

            let x = ((monitor_size.width as i32) - (target_width as i32)) / 2;
            let y = (10.0 * scale_factor) as i32;

            let _ = window.set_size(Size::Physical(PhysicalSize {
                width: target_width,
                height: target_height,
            }));

            let _ = window.set_position(Position::Physical(PhysicalPosition { x, y }));
            let _ = window.set_always_on_top(true);
            let _ = window.show();
            if expanded {
                let _ = window.set_focus();
            }
        }
    }
    Ok(())
}

pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            if let Some(window) = app.get_webview_window("island") {
                if let Ok(Some(monitor)) = window.primary_monitor() {
                    let monitor_size = monitor.size();
                    let scale_factor = monitor.scale_factor();
                    let target_width = (360.0 * scale_factor) as u32;
                    let target_height = (80.0 * scale_factor) as u32;

                    let x = ((monitor_size.width as i32) - (target_width as i32)) / 2;
                    let y = (10.0 * scale_factor) as i32;

                    let _ = window.set_size(Size::Physical(PhysicalSize {
                        width: target_width,
                        height: target_height,
                    }));
                    let _ = window.set_position(Position::Physical(PhysicalPosition { x, y }));
                }
                let _ = window.set_always_on_top(true);
                let _ = window.show();
                let _ = window.set_focus();
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![set_island_expanded])
        .run(tauri::generate_context!())
        .expect("error while running island agent");
}
