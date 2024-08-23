def zz_index_8x8(index: int):
    """
    Calculates x and y index for zig-zag traversal for the i-th index for a 8x8 matrix

    Args:
    - i: index

    Returns: x and y index for zig-zag traversal for the i-th index
    """

    # calculate in which diagonal counted from the top left corner the number resides
    ROW_STARTS = [1, 2, 4, 7, 11, 16, 22, 29, 37, 44, 50, 55, 59, 62, 64, 65]
    diagonal = 0
    for i, row_start in enumerate(ROW_STARTS):
        if not index >= row_start - 1:
            diagonal = i - 1
            break

    # calculate the index of the number within the diagonal row
    diagnoal_index = index - (ROW_STARTS[diagonal] - 1)

    # if the diagonal is going from left bottom to right top
    if diagonal % 2 == 0:
        # calculate the diagonal start indices
        diagonal_start_x = diagonal if diagonal < 8 else 7
        diagonal_start_y = 0 if diagonal < 8 else diagonal - 7

        # return the with the offset from the start indices
        return (diagonal_start_x - diagnoal_index, diagonal_start_y + diagnoal_index)

    # if the diagonal is going from right top to left bottom
    else:
        # calculate the diagonal start indices
        diagonal_start_x = 0 if diagonal < 8 else diagonal - 7
        diagonal_start_y = diagonal if diagonal < 8 else 7

        # return the with the offset from the start indices
        return (diagonal_start_x + diagnoal_index, diagonal_start_y - diagnoal_index)
