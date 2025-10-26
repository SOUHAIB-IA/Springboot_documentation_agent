from pydantic import BaseModel, Field

class ReadFileArgs(BaseModel):
    file_path: str = Field(description="The relative path to the file that needs to be read.")

class WriteFileArgs(BaseModel):
    file_path: str = Field(description="The relative path to the file that needs to be written.")
    content: str = Field(description="The new content to write to the file.")

class SaveMemoryArgs(BaseModel):
    content: str = Field(description="The piece of documentation or analysis to remember.")
    source_file: str = Field(description="The source file from which the content was derived.")

class SearchMemoryArgs(BaseModel):
    query: str = Field(description="The topic or question to search for in the memory.")


class EmptyArgs(BaseModel):
    """An explicit empty model for tools that accept no arguments.

    Using this avoids accidental inclusion of 'self' or other parameters
    in auto-generated schemas for instance methods.
    """
    pass