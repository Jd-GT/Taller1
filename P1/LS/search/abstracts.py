from abc import ABC, abstractmethod

class DataLoader(ABC):
    @abstractmethod
    def load_data(self):
        """Método abstracto para cargar datos de búsqueda."""
        pass