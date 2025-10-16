import asyncio
from typing import Dict, Any
import logging

logger=logging.getLogger(__name__)

class CommandDispatcher:
    def __init__(self, navigator, path_planner, telemetry):
        self.navigator=navigator
        self.planner=path_planner
        self.telemetry=telemetry
        self.current_mission=None
    
    async def handle_new_order(self, address: str) -> str:
        try:
            logger.info(f"New order received: {address}")
            
            route=await asyncio.to_thread(self.planner.get_route_to_address, address)
            
            if not route or len(route)==0:
                return "Не удалось построить маршрут до указанного адреса"
            
            self.current_mission={'type': 'address', 'destination': address, 'route': route}
            
            self.navigator.set_route(route)
            
            distance=route.get('distance', 'unknown')
            duration=route.get('duration', 'unknown')
            
            return (f"Маршрут построен до: {address}\n"
                   f"Расстояние: {distance}м\n"
                   f"Время: {duration}мин\n"
                   f"Начинаю движение...")
        
        except Exception as e:
            logger.error(f"Error in handle_new_order: {e}")
            raise
    
    async def handle_new_order_coordinates(self, lat: float, lon: float) -> str:
        try:
            logger.info(f"New order by coordinates: {lat}, {lon}")
            
            route=await asyncio.to_thread(self.planner.get_route_to_coordinates, lat, lon)
            
            if not route or len(route)==0:
                return "Не удалось построить маршрут до указанных координат"
            
            self.current_mission={'type': 'coordinates', 'destination': (lat, lon), 'route': route}
            
            self.navigator.set_route(route)
            
            distance=route.get('distance', 'unknown')
            duration=route.get('duration', 'unknown')
            
            return (f"Маршрут построен до: {lat}, {lon}\n"
                   f"Расстояние: {distance}м\n"
                   f"Время: {duration}мин\n"
                   f"Начинаю движение...")
        
        except Exception as e:
            logger.error(f"Error in handle_new_order_coordinates: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        try:
            nav_status=self.navigator.get_status()
            telemetry_data=self.telemetry.get_latest()
            
            return {
                'battery': telemetry_data.get('battery', 0),
                'position': telemetry_data.get('position', [0, 0]),
                'status': nav_status.get('state', 'idle'),
                'target': self.current_mission.get('destination', 'нет') if self.current_mission else 'нет',
                'distance_remaining': nav_status.get('distance_remaining', 0)
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return {'status': 'error', 'message': str(e)}
    
    async def cancel_mission(self) -> str:
        try:
            if self.current_mission is None:
                return "Нет активной миссии"
            
            self.navigator.stop()
            mission_dest=self.current_mission.get('destination', 'unknown')
            self.current_mission=None
            
            return f"Миссия отменена. Остановка. Цель была: {mission_dest}"
        
        except Exception as e:
            logger.error(f"Error cancelling mission: {e}")
            return f"Ошибка при отмене миссии: {str(e)}"