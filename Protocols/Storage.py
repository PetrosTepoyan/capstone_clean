from abc import ABC, abstractmethod

class Storage(ABC):
    @abstractmethod
    def initialize(self):
        """
        Abstract method for initializing the storage mechanism.
        Subclasses must implement this method.
        """
        pass
    
    @abstractmethod
    def close_file(self):
        "This method should close the file"
        pass

    @abstractmethod
    def append(self, data_dict):
        """
        Abstract method for storing data in the storage mechanism.
        Subclasses must implement this method.

        Args:
            data: The data to be stored.
        """
        pass

    @abstractmethod
    def path(self):
        """
        Abstract method for getting the path or location of the stored data.
        Subclasses must implement this method.

        Returns:
            str: The path or location of the stored data.
        """
        pass
